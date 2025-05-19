/** @type {import('tailwindcss').Config} */
module.exports =  {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    safelist: ['font-faculty'],
    theme: {
        extend: {
            // fontFamily: {
            //     inter: ['Inter', 'sans-serif'],
            //     faculty: ['Faculty Glyphic', 'sans-serif'],
            // },
        },
    },
        plugins: [],
    }