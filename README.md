# Recommendation System API

This project provides a RESTful API for a recommendation system, designed to process and serve recommendations based on market basket analysis and other data-driven techniques.

## Features
- Market basket analysis using association rules
- Data processing pipeline for raw and processed data
- Modular code structure for easy extension
- Jupyter notebooks for exploratory data analysis (EDA)

## Project Structure

```
├── main.py                  # Entry point for running the API
├── pyproject.toml           # Project dependencies and configuration
├── README.md                # Project documentation
├── data/
│   ├── 01_raw/              # Raw input data
│   └── 02_processed/        # Processed data (e.g., market_basket_results.csv)
├── models/                  # Saved models and artifacts
├── notebooks/
│   └── 01_EDA.ipynb         # Exploratory Data Analysis notebook
└── src/
	 ├── __init__.py
	 ├── api.py               # API endpoints and logic
	 └── data_processing.py   # Data loading and processing functions
```

## Setup

1. **Clone the repository:**
	```bash
	git clone github.com/metedogan/recomendation-system-api
	cd recomendation-system-api
	```

2. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	# or, if using pyproject.toml
	pip install .
	```

3. **Prepare data:**
	- Place your raw data files in `data/01_raw/`.
	- Processed data will be saved in `data/02_processed/`.

## Usage

### Run the API

```bash
python main.py
```
The API will start and listen for incoming requests. You can interact with it using tools like [curl](https://curl.se/) or [Postman](https://www.postman.com/).

### Data Processing

Data processing scripts are located in `src/data_processing.py`. You can use these to preprocess your data before running the API.

### Exploratory Data Analysis

Jupyter notebooks for EDA are available in the `notebooks/` directory. Open them with Jupyter Lab or Jupyter Notebook:

```bash
jupyter lab notebooks/01_EDA.ipynb
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License.
