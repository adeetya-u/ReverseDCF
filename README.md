# Valuing Consistent Compounders

## Overview

This Dash application provides tools for investors to calculate the intrinsic PE of consistent compounders through a growth-RoCE DCF model. By comparing this with the current PE of the stock, users can assess the degree of overvaluation. The application scrapes relevant financial data and metrics to perform its calculations and provides a user-friendly interface for interactive analysis.

## Features

- Calculation of intrinsic PE using the growth-RoCE DCF model.
- Comparison with current PE to assess overvaluation.
- Interactive sliders to adjust parameters such as Cost of Capital, RoCE, Growth Rate, and more.
- Visualizations of sales and profit growth.
- Display of current financial metrics and ratios.

## Installation

To run this application, you will need Python and pip installed on your system. It is recommended to use a virtual environment for Python projects to manage dependencies efficiently.

1. Clone or download this repository to your local machine.
2. Navigate to the project directory in your terminal.
3. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

4. Activate the virtual environment:

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

   - On Windows:

     ```cmd
     .\venv\Scripts\activate
     ```

5. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

With the virtual environment activated and dependencies installed, you can run the application using the following command:

```bash
python app.py
```

This will start a local server. Open a web browser and navigate to `http://127.0.0.1:8050/` to view and interact with the application.

## License

Open-Source under MIT license

---

For more information on how to use the application or contribute, please contact adeetya@purdue.edu
