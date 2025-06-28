# Open Filament Database - WebUI

A modern CRUD (Create, Read, Update, Delete) interface built with SvelteKit for managing the Open Filament Database. This web application provides an intuitive way to browse, add, edit, and manage filament data from various manufacturers.

## 🚀 Features

- **Browse Filament Database**: View all available filament brands, materials, and variants
- **CRUD Operations**: Create, read, update, and delete filament data
- **Modern UI**: Built with SvelteKit and TailwindCSS for a responsive, modern interface
- **Real-time Validation**: Data validation using JSON schemas
- **Export Functionality**: Export data as JSON files
- **Manufacturer Management**: Add and manage filament brands and their product lines

## 🌐 Usage Options

### Option 1: Online Version (Recommended for Browsing)

Simply visit the online version of the WebUI to browse the existing filament database. This is perfect for:

- Browsing available filaments
- Finding print profiles for your slicer
- Discovering new filament brands and materials

> **Note**: The online version URL will be provided once deployed.

### Option 2: Local Development (For Contributors)

Fork this repository and run your own instance locally. This option is ideal for:

- Adding new filament data
- Testing changes before submitting
- Creating custom JSON files based on existing data
- Contributing to the database

## 🛠️ Local Development Setup

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn package manager
- Git

### Installation

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/open-filament-database.git
   cd open-filament-database/webui
   ```

2. **Install Dependencies**

   ```bash
   npm install
   ```

3. **Start Development Server**

   ```bash
   npm run dev
   ```

4. **Open in Browser**
   Navigate to `http://localhost:5173` to access the WebUI.

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run check` - Run TypeScript and Svelte checks

## 📁 Data Structure

The WebUI works with the filament data located in the `/data` folder at the project root. The structure follows this hierarchy:

```
data/
├── [Brand Name]/
│   ├── brand.json          # Brand information
│   ├── [brand_logo.png]    # Brand logo
│   └── [Material Type]/    # e.g., PLA, ABS, PETG
│       ├── material.json   # Material settings
│       └── [Variant]/      # e.g., Basic, Silk, Carbon Fiber
│           ├── variant.json
│           ├── sizes.json
│           └── stores.json
```

### Key Files

- **`brand.json`**: Contains brand information (name, website, logo, origin)
- **`material.json`**: Contains material-specific settings and slicer profiles
- **`variant.json`**: Contains variant-specific properties (colors, special characteristics)
- **`sizes.json`**: Available sizes and specifications
- **`stores.json`**: Store availability and pricing information

## 🔧 Adding New Data

### Through the WebUI

1. Start the local development server
2. Navigate to the appropriate section (Brands, Materials, Variants)
3. Use the "Add New" buttons to create entries
4. Fill in the required information using the form interface
5. The WebUI will validate your data against the JSON schemas

### Manual JSON Creation

You can also create JSON files manually based on existing examples in the `/data` folder. Ensure your data follows the schemas defined in `/schemas/`.

## 📤 Contributing Your Data

After adding your filament data locally:

1. **Test Your Changes**

   ```bash
   npm run dev
   # Verify your data appears correctly in the WebUI
   ```

2. **Validate Data**
   The project includes validation scripts to ensure data integrity:

   ```bash
   # From the project root
   python data_validator.py
   ```

3. **Create a Pull Request**
   - Commit your changes to your forked repository
   - Create a Pull Request to the main repository
   - The automated checks will validate your data
   - Once approved, your data will be merged into the main database

## 🧪 Technology Stack

- **Frontend Framework**: SvelteKit 2.x
- **Styling**: TailwindCSS 4.x with custom forms and typography
- **Form Handling**: Sveltekit Superforms with Zod validation
- **Build Tool**: Vite 6.x
- **Language**: TypeScript

## 📝 Data Validation

The WebUI uses JSON schemas located in `/schemas/` to validate all data:

- `brand_schema.json` - Brand information validation
- `material_schema.json` - Material properties validation
- `variant_schema.json` - Variant details validation
- `sizes_schema.json` - Size specifications validation
- `store_schema.json` - Store information validation

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Add Filament Data**: Use the WebUI to add missing filaments from your collection
2. **Improve Documentation**: Help improve this README or add inline documentation
3. **Report Issues**: Found a bug? Report it in the GitHub issues
4. **Feature Requests**: Suggest new features for the WebUI

### Contribution Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes using the WebUI
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is open source. Please check the LICENSE file in the root directory for specific licensing information.

## 🆘 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/SimplyPrint/open-filament-database/issues)
- **Discussions**: Join the community discussions for questions and support

## 🔗 Related Links

- [Main Repository](https://github.com/SimplyPrint/open-filament-database)
- [SimplyPrint](https://simplyprint.io) - The organization behind this project

---

**Made with ❤️ by the SimplyPrint community**
