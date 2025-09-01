BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Medicine_inventory_medicine" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "brand" varchar(100) NOT NULL, "category" varchar(50) NOT NULL, "description" text NOT NULL, "dosage" varchar(50) NOT NULL, "quantity_in_stock" integer unsigned NOT NULL CHECK ("quantity_in_stock" >= 0), "reorder_level" integer unsigned NOT NULL CHECK ("reorder_level" >= 0), "manufacture_date" date NOT NULL, "expiry_date" date NOT NULL, "batch_number" varchar(150) NOT NULL UNIQUE, "supplier" varchar(100) NOT NULL, "medicine_type" varchar(10) NOT NULL, "cost_price" decimal NOT NULL, "selling_price" decimal NOT NULL, "image" varchar(100) NULL);
CREATE TABLE IF NOT EXISTS "Medicine_inventory_medicineaction" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(10) NOT NULL, "timestamp" datetime NOT NULL, "medicine_id" bigint NULL REFERENCES "Medicine_inventory_medicine" ("id") DEFERRABLE INITIALLY DEFERRED, "batch_number" varchar(255) NULL, "medicine_name" varchar(255) NULL, "user_id" bigint NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "Non_Medicine_inventory_nonmedicalproduct" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL, "slug" varchar(255) NOT NULL UNIQUE, "category" varchar(50) NOT NULL, "description" text NULL, "cost_price" decimal NOT NULL, "selling_price" decimal NOT NULL, "stock" integer unsigned NOT NULL CHECK ("stock" >= 0), "image" varchar(100) NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "reorder_level" integer unsigned NOT NULL CHECK ("reorder_level" >= 0), "brand" varchar(255) NOT NULL);
CREATE TABLE IF NOT EXISTS "accounts_customer" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "phone" varchar(15) NULL, "address" text NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "accounts_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "role" varchar(20) NOT NULL);
CREATE TABLE IF NOT EXISTS "accounts_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "accounts_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);
CREATE TABLE IF NOT EXISTS "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);
CREATE TABLE IF NOT EXISTS "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);
CREATE TABLE IF NOT EXISTS "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);
CREATE TABLE IF NOT EXISTS "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);
CREATE TABLE IF NOT EXISTS "payments_payment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "total_amount" decimal NOT NULL, "status" varchar(20) NOT NULL, "payment_date" datetime NOT NULL, "patient_id" bigint NOT NULL REFERENCES "prescriptions_patient" ("id") DEFERRABLE INITIALLY DEFERRED, "prescription_id" bigint NOT NULL REFERENCES "prescriptions_prescription" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "payments_paymentitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "price" decimal NOT NULL, "total_price" decimal NOT NULL, "medicine_id" bigint NOT NULL REFERENCES "Medicine_inventory_medicine" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_id" bigint NOT NULL REFERENCES "payments_payment" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "prescriptions_doctor" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "first_name" varchar(100) NOT NULL, "last_name" varchar(100) NOT NULL, "specialization" varchar(100) NULL, "contact_number" varchar(20) NULL, "medical_code" varchar(50) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS "prescriptions_druginteraction" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "drug1_name" varchar(255) NOT NULL, "drug2_name" varchar(255) NOT NULL, "interaction_description" text NOT NULL, "severity" varchar(50) NULL);
CREATE TABLE IF NOT EXISTS "prescriptions_patient" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "first_name" varchar(100) NOT NULL, "last_name" varchar(100) NOT NULL, "date_of_birth" date NOT NULL, "contact_number" varchar(20) NULL, "address" text NULL, "email" varchar(254) NULL);
CREATE TABLE IF NOT EXISTS "prescriptions_prescription" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "prescription_date" date NOT NULL, "notes" text NULL, "is_validated" bool NOT NULL, "interaction_warning" text NULL, "doctor_id" bigint NOT NULL REFERENCES "prescriptions_doctor" ("id") DEFERRABLE INITIALLY DEFERRED, "patient_id" bigint NOT NULL REFERENCES "prescriptions_patient" ("id") DEFERRABLE INITIALLY DEFERRED, "is_paid" bool NOT NULL);
CREATE TABLE IF NOT EXISTS "prescriptions_prescriptionitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "dosage" varchar(100) NOT NULL, "duration" varchar(100) NOT NULL, "requested_quantity" integer unsigned NOT NULL CHECK ("requested_quantity" >= 0), "dispensed_quantity" integer unsigned NOT NULL CHECK ("dispensed_quantity" >= 0), "medicine_id" bigint NOT NULL REFERENCES "Medicine_inventory_medicine" ("id") DEFERRABLE INITIALLY DEFERRED, "prescription_id" bigint NOT NULL REFERENCES "prescriptions_prescription" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "Medicine_inventory_medicine" ("id","name","brand","category","description","dosage","quantity_in_stock","reorder_level","manufacture_date","expiry_date","batch_number","supplier","medicine_type","cost_price","selling_price","image") VALUES (1,'Panadolll','Novartis','Antihistamine','test','10ml',200,10,'2025-08-29','2025-08-15','ANTIH-20250829-HENRY-001','AmerisourceBergen','RX',40,55.55,'non_medical_products/Slide5.png'),
 (2,'Aspirins','Panadol','Antipyretic','test','15ml',73,10,'2025-08-30','2026-04-10','ANTIP-20250830-SUN-001','Cipla Distributors','OTC',40,60,'medical_products/Slide9.png');
INSERT INTO "Medicine_inventory_medicineaction" ("id","action","timestamp","medicine_id","batch_number","medicine_name","user_id") VALUES (1,'created','2025-08-29 14:00:54.784185',1,'ANTIH-20250829-HENRY-001','Panadol',NULL),
 (2,'updated','2025-08-29 18:49:13.985021',1,'ANTIH-20250829-HENRY-001','Panadol',NULL),
 (3,'updated','2025-08-29 18:59:26.976839',1,'ANTIH-20250829-HENRY-001','Panadol',NULL),
 (4,'updated','2025-08-29 19:08:32.157322',1,'ANTIH-20250829-HENRY-001','Panadol',NULL),
 (5,'created','2025-08-29 19:14:56.482116',2,'ANTIP-20250830-SUN-001','Aspirin',NULL),
 (6,'updated','2025-08-29 19:55:20.221544',2,'ANTIP-20250830-SUN-001','Aspirins',NULL),
 (7,'update','2025-08-30 06:36:30.363630',2,NULL,NULL,NULL),
 (8,'update','2025-08-30 06:37:56.985392',2,NULL,NULL,NULL),
 (9,'update','2025-08-30 17:01:05.839153',2,NULL,NULL,NULL),
 (10,'update','2025-08-30 18:12:18.540055',2,NULL,NULL,19),
 (11,'update','2025-08-30 18:12:51.341792',1,NULL,NULL,19);
INSERT INTO "Non_Medicine_inventory_nonmedicalproduct" ("id","name","slug","category","description","cost_price","selling_price","stock","image","is_active","created_at","updated_at","reorder_level","brand") VALUES (1,'Soap','baby-cheramy-soap','Baby Products','test',20,35,100,'non_medical_products/3_pGyDYzI.png',1,'2025-08-29 18:36:22.342225','2025-08-30 06:28:31.997089',5,'Baby Cheramy'),
 (2,'Diaper','baby-care-diaper','Personal care','test',34,45,100,'non_medical_products/UseCase-Page-1_4LoQ2HG.drawio.png',1,'2025-08-30 06:15:48.539637','2025-08-30 06:28:20.582580',5,'Baby Care');
INSERT INTO "accounts_customer" ("id","phone","address","user_id") VALUES (4,NULL,'',20);
INSERT INTO "accounts_user" ("id","password","last_login","is_superuser","username","first_name","last_name","email","is_staff","is_active","date_joined","role") VALUES (8,'pbkdf2_sha256$1000000$RWsa6Sh2FhTlQFXcSmO1rG$9lyEGydUc149zlSemZzatFMfwD7loHC4Rhn1+O6DU2g=','2025-08-31 08:24:52.834660',1,'yoosuf1','','','yahamed95@gmail.com',1,1,'2025-08-30 16:50:00','admin'),
 (19,'pbkdf2_sha256$1000000$2a8bbBahZrLg3dia87aglt$OtLdRD03WllKufuRmPD3sof2shPXILg288+W3z5ZEy8=','2025-08-31 08:21:28.288100',0,'pharmacy','','','yahamed95@gmail.com',0,1,'2025-08-30 17:45:28.477242','pharmacist'),
 (20,'pbkdf2_sha256$1000000$RSDuK7mfTNSPRzalYd0nVz$8MYTHqVCFJ8nbJt/ZJPdVwcH7GL/ZlJJXUA+HAGMVbs=','2025-08-31 08:20:49.243883',0,'customer_yoosuf','','','testadmin@technest.com',0,1,'2025-08-30 18:20:00.150689','customer'),
 (21,'pbkdf2_sha256$1000000$KxS6ACdGvXMIsbGkplF2cI$BlTnAFbiDMbsPjpmN2e7x+/OH/NkkHZ0DcwwC+OU4c0=','2025-08-31 08:41:41.667873',0,'pharmacy2','','','pharmacyuser2@gmail.com',0,1,'2025-08-31 08:21:57.868855','pharmacist');
INSERT INTO "auth_permission" ("id","content_type_id","codename","name") VALUES (1,1,'add_logentry','Can add log entry'),
 (2,1,'change_logentry','Can change log entry'),
 (3,1,'delete_logentry','Can delete log entry'),
 (4,1,'view_logentry','Can view log entry'),
 (5,2,'add_permission','Can add permission'),
 (6,2,'change_permission','Can change permission'),
 (7,2,'delete_permission','Can delete permission'),
 (8,2,'view_permission','Can view permission'),
 (9,3,'add_group','Can add group'),
 (10,3,'change_group','Can change group'),
 (11,3,'delete_group','Can delete group'),
 (12,3,'view_group','Can view group'),
 (13,4,'add_contenttype','Can add content type'),
 (14,4,'change_contenttype','Can change content type'),
 (15,4,'delete_contenttype','Can delete content type'),
 (16,4,'view_contenttype','Can view content type'),
 (17,5,'add_session','Can add session'),
 (18,5,'change_session','Can change session'),
 (19,5,'delete_session','Can delete session'),
 (20,5,'view_session','Can view session'),
 (21,6,'add_medicine','Can add medicine'),
 (22,6,'change_medicine','Can change medicine'),
 (23,6,'delete_medicine','Can delete medicine'),
 (24,6,'view_medicine','Can view medicine'),
 (25,7,'add_medicineaction','Can add medicine action'),
 (26,7,'change_medicineaction','Can change medicine action'),
 (27,7,'delete_medicineaction','Can delete medicine action'),
 (28,7,'view_medicineaction','Can view medicine action'),
 (29,8,'add_doctor','Can add doctor'),
 (30,8,'change_doctor','Can change doctor'),
 (31,8,'delete_doctor','Can delete doctor'),
 (32,8,'view_doctor','Can view doctor'),
 (33,9,'add_patient','Can add patient'),
 (34,9,'change_patient','Can change patient'),
 (35,9,'delete_patient','Can delete patient'),
 (36,9,'view_patient','Can view patient'),
 (37,10,'add_druginteraction','Can add drug interaction'),
 (38,10,'change_druginteraction','Can change drug interaction'),
 (39,10,'delete_druginteraction','Can delete drug interaction'),
 (40,10,'view_druginteraction','Can view drug interaction'),
 (41,11,'add_prescription','Can add prescription'),
 (42,11,'change_prescription','Can change prescription'),
 (43,11,'delete_prescription','Can delete prescription'),
 (44,11,'view_prescription','Can view prescription'),
 (45,12,'add_prescriptionitem','Can add prescription item'),
 (46,12,'change_prescriptionitem','Can change prescription item'),
 (47,12,'delete_prescriptionitem','Can delete prescription item'),
 (48,12,'view_prescriptionitem','Can view prescription item'),
 (49,13,'add_nonmedicalproduct','Can add Non-Medical Product'),
 (50,13,'change_nonmedicalproduct','Can change Non-Medical Product'),
 (51,13,'delete_nonmedicalproduct','Can delete Non-Medical Product'),
 (52,13,'view_nonmedicalproduct','Can view Non-Medical Product'),
 (53,14,'add_payment','Can add payment'),
 (54,14,'change_payment','Can change payment'),
 (55,14,'delete_payment','Can delete payment'),
 (56,14,'view_payment','Can view payment'),
 (57,15,'add_paymentitem','Can add payment item'),
 (58,15,'change_paymentitem','Can change payment item'),
 (59,15,'delete_paymentitem','Can delete payment item'),
 (60,15,'view_paymentitem','Can view payment item'),
 (61,16,'add_user','Can add user'),
 (62,16,'change_user','Can change user'),
 (63,16,'delete_user','Can delete user'),
 (64,16,'view_user','Can view user'),
 (65,17,'add_customer','Can add customer'),
 (66,17,'change_customer','Can change customer'),
 (67,17,'delete_customer','Can delete customer'),
 (68,17,'view_customer','Can view customer');
INSERT INTO "django_admin_log" ("id","object_id","object_repr","action_flag","change_message","content_type_id","user_id","action_time") VALUES (12,'8','yoosuf1 (admin)',2,'[{"changed": {"fields": ["Role"]}}]',16,8,'2025-08-30 16:50:28.229126'),
 (13,'3','yoosuf_admin1 (admin)',3,'',16,8,'2025-08-30 16:50:52.221434'),
 (14,'9','admin (admin)',1,'[{"added": {}}]',16,8,'2025-08-30 16:54:21.909568'),
 (15,'10','pharmacy (pharmacist)',1,'[{"added": {}}]',16,8,'2025-08-30 16:57:55.403850'),
 (16,'9','admin (admin)',3,'',16,8,'2025-08-30 17:43:35.904416'),
 (17,'16','husaifa.admin (admin)',3,'',16,8,'2025-08-30 17:43:35.904457'),
 (18,'13','husaifa.customer (customer)',3,'',16,8,'2025-08-30 17:43:35.904472'),
 (19,'18','yoosuf.ahamed (pharmacist)',3,'',16,8,'2025-08-30 17:43:35.904486');
INSERT INTO "django_content_type" ("id","app_label","model") VALUES (1,'admin','logentry'),
 (2,'auth','permission'),
 (3,'auth','group'),
 (4,'contenttypes','contenttype'),
 (5,'sessions','session'),
 (6,'Medicine_inventory','medicine'),
 (7,'Medicine_inventory','medicineaction'),
 (8,'prescriptions','doctor'),
 (9,'prescriptions','patient'),
 (10,'prescriptions','druginteraction'),
 (11,'prescriptions','prescription'),
 (12,'prescriptions','prescriptionitem'),
 (13,'Non_Medicine_inventory','nonmedicalproduct'),
 (14,'payments','payment'),
 (15,'payments','paymentitem'),
 (16,'accounts','user'),
 (17,'accounts','customer');
INSERT INTO "django_migrations" ("id","app","name","applied") VALUES (1,'Medicine_inventory','0001_initial','2025-08-29 13:07:13.065747'),
 (2,'Medicine_inventory','0002_alter_medicine_category','2025-08-29 13:07:13.067416'),
 (3,'Medicine_inventory','0003_alter_medicine_batch_number_alter_medicine_category','2025-08-29 13:07:13.069827'),
 (4,'Medicine_inventory','0004_medicineaction','2025-08-29 13:07:13.071691'),
 (5,'Medicine_inventory','0005_alter_medicineaction_action_and_more','2025-08-29 13:07:13.075151'),
 (6,'Medicine_inventory','0006_medicineaction_batch_number_and_more','2025-08-29 13:07:13.078315'),
 (7,'Medicine_inventory','0007_medicine_medicine_type','2025-08-29 13:07:13.080264'),
 (8,'Medicine_inventory','0008_remove_medicine_price_medicine_cost_price_and_more','2025-08-29 13:07:13.085675'),
 (9,'Medicine_inventory','0009_alter_medicine_medicine_type','2025-08-29 13:07:13.088038'),
 (10,'Non_Medicine_inventory','0001_initial','2025-08-29 13:07:13.089275'),
 (11,'Non_Medicine_inventory','0002_nonmedicalproduct_brand','2025-08-29 13:07:13.091013'),
 (12,'Non_Medicine_inventory','0003_alter_nonmedicalproduct_brand','2025-08-29 13:07:13.093256'),
 (13,'contenttypes','0001_initial','2025-08-29 13:07:13.094792'),
 (14,'contenttypes','0002_remove_content_type_name','2025-08-29 13:07:13.098760'),
 (15,'auth','0001_initial','2025-08-29 13:07:13.103137'),
 (16,'auth','0002_alter_permission_name_max_length','2025-08-29 13:07:13.105642'),
 (17,'auth','0003_alter_user_email_max_length','2025-08-29 13:07:13.107287'),
 (18,'auth','0004_alter_user_username_opts','2025-08-29 13:07:13.109174'),
 (19,'auth','0005_alter_user_last_login_null','2025-08-29 13:07:13.111009'),
 (20,'auth','0006_require_contenttypes_0002','2025-08-29 13:07:13.112139'),
 (21,'auth','0007_alter_validators_add_error_messages','2025-08-29 13:07:13.114888'),
 (22,'auth','0008_alter_user_username_max_length','2025-08-29 13:07:13.116418'),
 (23,'auth','0009_alter_user_last_name_max_length','2025-08-29 13:07:13.118135'),
 (24,'auth','0010_alter_group_name_max_length','2025-08-29 13:07:13.120444'),
 (25,'auth','0011_update_proxy_permissions','2025-08-29 13:07:13.122812'),
 (26,'auth','0012_alter_user_first_name_max_length','2025-08-29 13:07:13.124597'),
 (27,'accounts','0001_initial','2025-08-29 13:07:13.128848'),
 (28,'admin','0001_initial','2025-08-29 13:07:13.132805'),
 (29,'admin','0002_logentry_remove_auto_add','2025-08-29 13:07:13.136380'),
 (30,'admin','0003_logentry_add_action_flag_choices','2025-08-29 13:07:13.138953'),
 (31,'prescriptions','0001_initial','2025-08-29 13:07:13.145930'),
 (32,'prescriptions','0002_doctor_medical_code','2025-08-29 13:07:13.148510'),
 (33,'prescriptions','0003_prescription_is_paid','2025-08-29 13:07:13.189075'),
 (34,'payments','0001_initial','2025-08-29 13:07:13.194518'),
 (35,'prescriptions','0004_patient_email','2025-08-29 13:07:13.196651'),
 (36,'sessions','0001_initial','2025-08-29 13:07:13.198157'),
 (37,'Medicine_inventory','0010_medicine_image','2025-08-29 18:45:12.934083'),
 (38,'Medicine_inventory','0011_alter_medicine_image','2025-08-29 19:13:47.544943'),
 (39,'Non_Medicine_inventory','0004_alter_nonmedicalproduct_category','2025-08-30 06:21:39.271001'),
 (40,'Medicine_inventory','0012_medicineaction_user','2025-08-30 06:36:01.974605'),
 (41,'accounts','0002_customer','2025-08-30 16:26:42.728595');
INSERT INTO "django_session" ("session_key","session_data","expire_date") VALUES ('3omcv85ostm5zy48mtu12bkp7bxy07t9','.eJxVjMsOwiAQRf-FtSEwUh4u3fcbyJQZpGogKe3K-O_apAvd3nPOfYmI21ri1nmJM4mLAC1Ov-OE6cF1J3THemsytbou8yR3RR60y7ERP6-H-3dQsJdvrQGHYKzWAS0lj-ycUc4nUCEMIYNOOZ0hgyEyHBiMypaddy5TNopIvD_s9Dft:1usdd7:TFFyQ8NnbYRu_lAQuBaeSxCuNH8yzRQtnL6qpNCQ1lw','2025-09-14 08:41:41.668773');
CREATE INDEX "Medicine_inventory_medicineaction_medicine_id_2632f1f7" ON "Medicine_inventory_medicineaction" ("medicine_id");
CREATE INDEX "Medicine_inventory_medicineaction_user_id_3fa2452b" ON "Medicine_inventory_medicineaction" ("user_id");
CREATE INDEX "accounts_user_groups_group_id_bd11a704" ON "accounts_user_groups" ("group_id");
CREATE INDEX "accounts_user_groups_user_id_52b62117" ON "accounts_user_groups" ("user_id");
CREATE UNIQUE INDEX "accounts_user_groups_user_id_group_id_59c0b32f_uniq" ON "accounts_user_groups" ("user_id", "group_id");
CREATE INDEX "accounts_user_user_permissions_permission_id_113bb443" ON "accounts_user_user_permissions" ("permission_id");
CREATE INDEX "accounts_user_user_permissions_user_id_e4f0a161" ON "accounts_user_user_permissions" ("user_id");
CREATE UNIQUE INDEX "accounts_user_user_permissions_user_id_permission_id_2ab516c2_uniq" ON "accounts_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
CREATE INDEX "payments_payment_patient_id_699ec0ae" ON "payments_payment" ("patient_id");
CREATE INDEX "payments_payment_prescription_id_65c8f9f0" ON "payments_payment" ("prescription_id");
CREATE INDEX "payments_paymentitem_medicine_id_696844f5" ON "payments_paymentitem" ("medicine_id");
CREATE INDEX "payments_paymentitem_payment_id_cf9b51d2" ON "payments_paymentitem" ("payment_id");
CREATE UNIQUE INDEX "prescriptions_druginteraction_drug1_name_drug2_name_5e075181_uniq" ON "prescriptions_druginteraction" ("drug1_name", "drug2_name");
CREATE UNIQUE INDEX "prescriptions_druginteraction_drug2_name_drug1_name_d5da9c10_uniq" ON "prescriptions_druginteraction" ("drug2_name", "drug1_name");
CREATE INDEX "prescriptions_prescription_doctor_id_dc96730f" ON "prescriptions_prescription" ("doctor_id");
CREATE INDEX "prescriptions_prescription_patient_id_22183bec" ON "prescriptions_prescription" ("patient_id");
CREATE INDEX "prescriptions_prescriptionitem_medicine_id_ff7e9ad0" ON "prescriptions_prescriptionitem" ("medicine_id");
CREATE INDEX "prescriptions_prescriptionitem_prescription_id_89e3394e" ON "prescriptions_prescriptionitem" ("prescription_id");
CREATE UNIQUE INDEX "prescriptions_prescriptionitem_prescription_id_medicine_id_8623b30a_uniq" ON "prescriptions_prescriptionitem" ("prescription_id", "medicine_id");
COMMIT;
