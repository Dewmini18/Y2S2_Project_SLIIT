from email.message import EmailMessage
import io
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.conf import settings
from django.contrib import messages
from prompt_toolkit import HTML
import stripe
from prescriptions.models import Prescription, PrescriptionItem
from .models import *
from django.core.paginator import Paginator
from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.mail import send_mail

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_prescription(request, pk):
   
    prescription = get_object_or_404(Prescription, pk=pk)
    
    if not prescription.items.all().exists():
        messages.error(request, "This prescription is empty and cannot be processed for payment.")
        return redirect('prescription_detail', pk=pk)
        
    # --- Create a new Payment object in 'pending' status ---
    payment = Payment.objects.create(
        patient=prescription.patient,
        prescription=prescription,
        status='pending'
    )
    
    # Calculate the total amount and prepare line items for Stripe
    line_items = []
    for item in prescription.items.all():
        unit_amount = int(item.medicine.selling_price * 100)
        
        # --- Create a PaymentItem for each PrescriptionItem ---
        PaymentItem.objects.create(
            payment=payment,
            medicine=item.medicine,
            quantity=item.dispensed_quantity,
            price=item.medicine.selling_price
        )
        
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f"{item.medicine.name} ({item.medicine.dosage})",
                },
                'unit_amount': unit_amount,
            },
            'quantity': item.dispensed_quantity,
        })
    
    # Update the payment total
    payment.calculate_total()
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(f'http://127.0.0.1:8000/payments/success/{payment.pk}/'), 
            cancel_url=request.build_absolute_uri(f'http://127.0.0.1:8000/payments/cancelled/{payment.pk}/'),
            metadata={'payment_id': payment.id},
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        messages.error(request, f"An error occurred while creating the checkout session: {str(e)}")
        # If an error occurs, delete the pending payment and its items
        payment.delete()
        return redirect('prescription_detail', pk=pk)

def success_payment(request, pk):
    """
    Handles successful payment from Stripe.
    Updates the Payment object's status and shows a success message.
    """
    payment = get_object_or_404(Payment, pk=pk)
    payment.status = 'paid'
    payment.save()
    
    messages.success(request, f"Payment #{payment.id} for Prescription #{payment.prescription.id} was successful!")
    
    return redirect('payment_detail', pk=payment.pk)

def cancel_payment(request, pk):
    """
    Handles cancelled payment from Stripe.
    Deletes the Payment object and redirects to the payment list page.
    """
    payment = get_object_or_404(Payment, pk=pk)
    # The payment was cancelled, so we delete the pending record
    payment.delete()
    
    messages.info(request, "Payment was cancelled. You can try again.")
    return redirect('payment_list')

def payment_list(request):
    """
    Displays a paginated list of all payments.
    """
    payments = Payment.objects.all().order_by('-payment_date')
    
    # Set up pagination
    paginator = Paginator(payments, 10) # Show 10 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'payments/payment_list.html', context)

def payment_detail(request, pk):
    """
    Displays the details of a single payment.
    """
    payment = get_object_or_404(Payment, pk=pk)
    context = {
        'payment': payment,
        'payment_items': payment.payment_items.all(),
    }
    return render(request, 'payments/payment_detail.html', context)

def generate_invoice_pdf(request, pk):
    
    payment = get_object_or_404(Payment, pk=pk)
    
    prescription = get_object_or_404(Prescription.objects.prefetch_related('items__medicine'), pk=payment.prescription.pk)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Generate table rows for the invoice items
    table_rows = "".join([
        f"""
        <tr>
            <td>{item.medicine.name} ({item.medicine.batch_number})</td>
            <td>{item.dispensed_quantity}</td>
            <td class="price-cell">${item.medicine.selling_price:.2f}</td>
            <td class="price-cell">${item.total_price:.2f}</td>
        </tr>
        """ for item in prescription.items.all()
    ])

    # Get the payment status (e.g., 'Paid', 'Pending', 'Cancelled')
    # You'll need to update this part to match your Payment model's field
    payment_status = "Paid" # Placeholder, replace with your actual field

    # Construct the HTML content for the PDF, with improved styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice #{payment.id}</title>
        <style>
            @page {{
                size: a4;
                margin: 0.75in;
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 0;
                font-size: 10pt;
            }}
            .container {{
                width: 100%; /* Use 100% to fill the page, letting @page handle margins */
                max-width: 7in; /* A safe max-width for A4 */
                margin-left: auto;
                margin-right: auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20pt;
                padding-bottom: 10pt;
                border-bottom: 2px solid #333;
            }}
            .header h1 {{
                font-size: 24pt;
                margin: 0;
                color: #004d40;
            }}
            .header p {{
                font-size: 10pt;
                margin: 5pt 0 0;
                color: #555;
            }}
            .invoice-info {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30pt;
            }}
            .invoice-info div {{
                width: 48%;
            }}
            .invoice-info h2 {{
                font-size: 14pt;
                margin: 0 0 10pt;
                color: #004d40;
            }}
            .info-block p {{
                margin: 2pt 0;
                font-size: 10pt;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20pt;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10pt;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                color: #333;
                text-transform: uppercase;
            }}
            .price-cell {{
                text-align: right;
                font-weight: bold;
            }}
            .total-section {{
                text-align: right;
                font-size: 12pt;
                margin-top: 20pt;
            }}
            .total-section p {{
                font-size: 14pt;
                font-weight: bold;
                margin: 5pt 0;
            }}
            .total-section .label {{
                color: #555;
                font-weight: normal;
            }}
            .footer {{
                text-align: center;
                margin-top: 40pt;
                padding-top: 10pt;
                border-top: 1px solid #ddd;
                font-size: 9pt;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Pharmacy Rix</h1>
                <p>123 Medical Drive, Healthville, USA</p>
            </div>

            <div class="invoice-info">
                <div class="info-block">
                    <h2>Invoice To:</h2>
                    <p><strong>{prescription.patient.first_name} {prescription.patient.last_name}</strong></p>
                    <p>DOB: {prescription.patient.date_of_birth.strftime('%Y-%m-%d')}</p>
                </div>
                <div class="info-block" style="text-align: right;">
                    <h2>Invoice Details:</h2>
                    <p><strong>Invoice ID:</strong> INV-{payment.id}</p>
                    <p><strong>Status:</strong> {payment_status}</p>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            
            <div class="total-section">
                <p><span class="label">Total Amount:</span> ${prescription.total_cost:.2f}</p>
            </div>
            
            <div class="footer">
                <p>Thank you for your business. All payments are due upon receipt.</p>
                <p>For questions regarding this invoice, please contact us at support@pharmacyrix.com.</p>
            </div>
        </div>
    </body>
    </html>
    """

    
    # Generate the PDF into an in-memory buffer
    HTML(string=html_content).write_pdf(buffer)

    # Get the value of the BytesIO buffer and set up the HTTP response.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.id}.pdf"'
    return response



def send_invoice_email(request, pk):
    
    if request.method == 'POST':
        try:
            # First, retrieve the Payment object using get_object_or_404.
            # This is safer than a direct .get() call as it handles the case
            # where the payment doesn't exist.
            payment = get_object_or_404(Payment, pk=pk)

            # Now, get the associated patient. We can do this directly from the payment object
            # if the foreign key is set up correctly. Let's assume it's named 'patient'.
            # We use get_object_or_404 again to ensure the patient exists.
            patient = get_object_or_404(Patient, pk=payment.patient.pk)

            # You can also use a try-except block here for more specific handling
            # of the related object not existing.
            # try:
            #     patient = payment.patient
            # except Patient.DoesNotExist:
            #     messages.error(request, 'The patient for this payment does not exist.')
            #     return redirect('your_redirect_url')

            subject = 'Your Invoice from Our Clinic'
            html_message = render_to_string('payments/invoice_email_template.html', {
                'payment': payment,
                'patient': patient
            })
            
            send_mail(
                subject,
                'Please find your invoice attached.',
                settings.EMAIL_HOST_USER,
                [patient.email],
                html_message=html_message,
            )
            messages.success(request, 'Invoice email sent successfully!')

        except Exception as e:
            # Catch any other exceptions that might occur during the process.
            messages.error(request, f'Failed to send invoice email: {e}')

        return redirect('payment_detail', pk=pk)
