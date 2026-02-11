# Canada Agricultural Atlas

An interactive web application visualizing agricultural production patterns across all of Canada at the Census Division (ADM2) level.

![Canada Agricultural Atlas](screenshot.png)

## Features

- **National Coverage**: Visualize agricultural data for all Canadian provinces and territories
- **Multiple Product Categories**: Field crops, vegetables, fruits & berries, greenhouse products, livestock, poultry, and overall summaries
- **Two Analysis Modes**: 
  - Top Product per Region: See dominant products by area
  - Specific Product Distribution: Examine individual product distributions with continuous color scales
- **Province Filtering**: View specific provinces or all of Canada
- **Interactive Maps**: Color-coded choropleth maps with province boundary overlays on dark basemap
- **Advanced Visualizations**: 
  - Bar charts and bubble charts for production analysis
  - Sankey diagrams showing province-to-product or province-to-region flows
  - Provincial comparison charts
- **Data Export**: Download filtered data as CSV
- **Responsive Design**: Works on desktop and mobile

## Live Demo

**[View Live App](https://your-app-url.streamlit.app)**

## Data Methodology

Agricultural data from **Statistics Canada Agricultural Census**, processed using:
- Area-weighted proportional assignment for farms crossing administrative boundaries
- Conversion of square meter measurements to hectares for consistency
- Exclusion of aggregate totals to prevent dominance of summary statistics
- Categorization into specific product types with human-readable labels

## Local Development

### Prerequisites

- Python 3.8+
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/canada-ag-atlas.git
cd canada-ag-atlas

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure
```
canada-ag-atlas/
├── app.py                                      # Main Streamlit application
├── requirements.txt                            # Python dependencies
├── README.md                                   # Documentation
├── .gitignore                                 # Git ignore file
└── data/
    └── canada_adm2_agricultural_stats.gpkg    # Agricultural statistics by ADM2
```

## Technical Stack

- **Geospatial**: GeoPandas, Shapely
- **Visualization**: Folium (interactive maps), Plotly (charts), Branca (color scales)
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy

## Categories

### Crop Categories
- **Field Crops**: Wheat, canola, barley, oats, corn, soybeans, lentils, etc.
- **Vegetables**: Lettuce, carrots, tomatoes, peppers, potatoes, onions, etc.
- **Fruits & Berries**: Apples, blueberries, strawberries, grapes, cherries, etc.
- **Greenhouse Products**: Greenhouse tomatoes, cucumbers, peppers, flowers, herbs

### Livestock Categories
- **Livestock**: Beef cattle, dairy cows, pigs, sheep, goats, horses, bison, etc.
- **Poultry**: Broilers, laying hens, turkeys, ducks, geese

### Aggregate Categories
- **All Crops**: Overall dominant crop across all categories
- **All Animals**: Overall dominant animal production (livestock + poultry)

## Color Schemes

The application uses category-specific color palettes:
- **Categorical maps** (Top Product per Region): 10-color diverging palette
- **Continuous maps** (Specific Product Distribution): Category-specific sequential palettes
  - Field Crops & Livestock: Brown scale
  - Vegetables: Green scale
  - Fruits & Berries: Red scale
  - Greenhouse Products: Purple scale
  - Poultry: Orange scale

## Author

**Rex Devereux**  
Data Analyst & Geospatial Specialist

## License

MIT License - feel free to use this project for your own portfolio or applications.

## Acknowledgments

- Statistics Canada for agricultural census data
- Streamlit team for the excellent framework
- ColorBrewer for color scheme inspiration