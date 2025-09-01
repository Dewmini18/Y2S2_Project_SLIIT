import React from 'react'
import { data } from 'react-router-dom'

export const Navbar = () => {
    const MenuLinks = [
        { 
            id: 1,
            name: 'Home',
            link: '/#' },
        { 
            id: 2, 
            name: 'Store', 
            link: '/#Store' },
        { 
            id: 3, 
            name: 'About', 
            link: '/#About' },
        { 
            id: 4, 
            name: 'Contact', 
            link: '/#Contact' 
        },
    ];
  return (
    <div className='bg-white duration-200 relative z-40'>
        <div className='py-4 shadow-md'>
            <div className='container'>
                {/* Logo and Links Section */}
                <div className='flex items-center gap-4'>
                    <a href=""
                    className="text-primary
                    font-semibold tracking-widest text-2xl  uppercase
                    sm:text-3xl"
                    >MediSync</a>
                    {/* Menu Links */}
                    <div className='hidden lg:block'>
                        <ul className='flex items-center gap-4'>
                            {
                                MenuLinks.map((data, index) => (
                                    <li key={index}>
                                        <a href={data.link} className="inline-block px-4 
                                        font-semibold text-gray-500 hover:text-black duration-200">
                                            {data.name}
                                        </a>
                                    </li>
                                ))
                            }
                        </ul>
                    </div>

                </div>

                {/* Navbar right section */}
                <div>
                    {/* Search Bar */}
                    <div>
                        <input type="text" placeholder='Search' className=''/>
                    </div>
                </div>
            </div>
        </div>
    </div>
  )
}
