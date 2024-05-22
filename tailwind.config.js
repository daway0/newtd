/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["**/*.html"],
  theme: {
    extend: {
      colors: {
        // Existing Tailwind colors (optional)
        // gray: '#99a3b2', // Example: Override gray color

        // Your custom colors
        primary: '#075C95',
        secondary: '#E6EEF1',
        white: "#ffffff",
        searchbox: "#F8F8F8",
        cardtitle: "#4E4E4E",
        primarytext: "#073363",
        cardiconfill: "#89B5D1",
        seperatorline: "#E8E8E8",
        statcardborder: "#E6E6E6",
        black: "#1F2022",
        
        successtext: '#166534',
        successbg: '#dcfce7',

        infotext: '#075985',
        infobg: '#e0f2fe',

        errortext: '#991b1b',
        errorbg: '#fee2e2',

        failed:"#e04444",
        warning: '#ffc107',


        // ... Add more colors as needed
      },
    },

  },
}