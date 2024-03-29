import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
from scraper import scrape_market_cap_and_pe, scrape_roce_median, scrape_compounded_growth
from dash import dash_table
from pe_calc import calculate_intrinsic_value
import plotly.graph_objs as go

external_stylesheets = ['https://fonts.googleapis.com/css2?family=Nunito+Sans&display=swap']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div([

    html.H1('Valuing Consistent Compounders', style={'font-family': 'Nunito Sans', 'font-size': '24px', 'color': 'gray'}),
    html.P('This page will help you calculate intrinsic PE of consistent compounders through growth-RoCE DCF model. '
           'Compare this with current PE of the stock to calculate the degree of overvaluation.',
           style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),

    html.Div([
        html.Label('NSE/BSE Symbol:', style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
        dcc.Input(id='symbol-input', type='text', value='NESTLEIND', style={'margin-bottom': '20px'}),
    ]),

    html.Div([
        html.Label('Cost of Capital (CoC):',
                   style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
        dcc.Slider(id='coc-slider', min=8, max=16, step=0.5, value=10, marks={i: str(i) for i in range(8, 17)}),
    ]),

    html.Div([
        html.Label('Return on Capital Employed (RoCE):',
                   style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
        dcc.Slider(id='roce-slider', min=10, max=100, step=5, value=30, marks={i: str(i) for i in range(0, 101, 10)}),
    ]),

    html.Div([
        html.Label('Growth during high growth period (%):',
                   style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
        dcc.Slider(id='growth-slider', min=8, max=20, step=1, value=12, marks={i: str(i) for i in range(0, 21, 2)}),
    ]),

    html.Div([
        html.Label('High growth period (years):',
                   style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
        dcc.Slider(id='high-growth-period-slider', min=10, max=25, step=1, value=10,
                   marks={i: str(i) for i in range(0, 26, 2)} | {25: '25'}),
    ]),

    html.Div([
        html.Label('Fade period (years):', style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
        dcc.Slider(id='fade-period-slider', min=5, max=20, step=5, value=5, marks={i: str(i) for i in range(0, 26, 5)}),
    ]),

    html.Div([
        html.Label('Terminal growth rate (%):',
                   style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
        dcc.Slider(id='terminal-growth-slider', min=0, max=7.5, step=0.5, value=2,
                   marks={i: str(i) for i in range(0, 8, 1)} | {7.5: '7.5'}),
    ]),

    html.Div(id='stock-symbol', style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
    html.Div(id='current-pe', style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
    html.Div(id='fy23-pe', style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),
    html.Div(id='median-pre-tax-roce', style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'}),

    html.Div(id='growth-table-container'),  # Added for the growth table

    html.Div([
        html.Div([
            dcc.Graph(id='sales-growth-graph', style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(id='profit-growth-graph', style={'width': '48%', 'display': 'inline-block'})
        ])
    ]),

    html.Div(id='intrinsic-output', style={'font-family': 'Nunito Sans', 'font-size': '14px', 'color': 'gray'})

])


@app.callback(
    [Output('intrinsic-output', 'children'),
     Output('stock-symbol', 'children'),
     Output('current-pe', 'children'),
     Output('fy23-pe', 'children'),
     Output('median-pre-tax-roce', 'children')],
    [Input('symbol-input', 'value'),
     Input('coc-slider', 'value'),
     Input('roce-slider', 'value'),
     Input('growth-slider', 'value'),
     Input('high-growth-period-slider', 'value'),
     Input('fade-period-slider', 'value'),
     Input('terminal-growth-slider', 'value')],
    [State('intrinsic-output', 'children'),
     State('stock-symbol', 'children'),
     State('current-pe', 'children'),
     State('fy23-pe', 'children'),
     State('median-pre-tax-roce', 'children')]
)
def update_intrinsic(symbol, coc, roce, growth, high_growth_period, fade_period, terminal_growth,
                     intrinsic_output_prev, stock_symbol_prev, current_pe_prev, fy23_pe_prev, median_pre_tax_roce_prev):
    if symbol is None:  # If symbol is not provided, return previous values
        return intrinsic_output_prev, stock_symbol_prev, current_pe_prev, fy23_pe_prev, median_pre_tax_roce_prev

    try:
        scrap = scrape_market_cap_and_pe(symbol)
        if scrap is None or 'Stock P/E' not in scrap or 'FY23 P/E' not in scrap:
            raise ValueError("Invalid scraping result")

        current_pe = scrap['Stock P/E']
        fy23_pe = scrap['FY23 P/E']

        roce_data = scrape_roce_median(symbol)  # Ensure this function is defined to fetch ROCE data
        if roce_data is None:
            raise ValueError("Invalid ROCE scraping result")

        intrinsic_pe, overeval = calculate_intrinsic_value(roce, coc, growth, high_growth_period, fade_period,
                                                           terminal_growth, scrap)

        intrinsic_pe_output = html.Div([
            html.P(f"The Calculated Intrinsic PE: {round(intrinsic_pe, 2)}"),
            html.P(f"Degree of overvaluation: {round(overeval * 100)}%")
        ])

        stock_symbol_output = f"Stock Symbol: {symbol}"
        current_pe_output = f"Current PE: {current_pe}"
        fy23_pe_output = f"FY23 PE: {fy23_pe}"
        median_pre_tax_roce_output = f"5-yr median tax pre-roce: {roce_data}"

        return intrinsic_pe_output, stock_symbol_output, current_pe_output, fy23_pe_output, median_pre_tax_roce_output

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return html.Div(error_message), "", "", "", ""


@app.callback(
    Output('growth-table-container', 'children'),
    [Input('symbol-input', 'value')]
)
def update_growth_table(symbol):
    sales_growth_rates, profit_growth_rates = scrape_compounded_growth(symbol)

    if sales_growth_rates is not None and profit_growth_rates is not None:
        # Remove percentage signs from the data
        sales_growth_rates = [rate.replace('%', '') for rate in sales_growth_rates]
        profit_growth_rates = [rate.replace('%', '') for rate in profit_growth_rates]

        data = {
            '10 YRS': {'Sales Growth': sales_growth_rates[0], 'Profit Growth': profit_growth_rates[0]},
            '5 YRS': {'Sales Growth': sales_growth_rates[1], 'Profit Growth': profit_growth_rates[1]},
            '3 YRS': {'Sales Growth': sales_growth_rates[2], 'Profit Growth': profit_growth_rates[2]},
            'TTM': {'Sales Growth': sales_growth_rates[3], 'Profit Growth': profit_growth_rates[3]}
        }

        columns = [{'name': period, 'id': period} for period in data.keys()]
        rows = [{'Metric': metric, **{period: data[period][metric] for period in data.keys()}}
                for metric in ['Sales Growth', 'Profit Growth']]

        return dash_table.DataTable(
            id='growth-table',
            columns=[{'name': 'Metric', 'id': 'Metric'}] + columns,
            data=rows,
            style_table={'margin-top': '20px'}
        )
    else:
        return html.P("No growth rate data available for the specified symbol.")


@app.callback(
    Output('sales-growth-graph', 'figure'),
    [Input('symbol-input', 'value')]
)
def update_sales_graph(symbol):
    sales_growth_rates, _ = scrape_compounded_growth(symbol)
    if sales_growth_rates:
        # Convert growth rates to float and remove percentage signs
        sales_growth_rates = [float(rate.replace('%', '')) for rate in sales_growth_rates]

        # Create bar chart for sales growth
        figure = {
            'data': [go.Bar(
                y=['10 yrs', '5 yrs', '3 yrs', 'TTM'],
                x=sales_growth_rates,
                orientation='h'
            )],
            'layout': go.Layout(
                title='Sales Growth',
                yaxis=dict(title='Time Period'),
                xaxis=dict(title='Sales Growth (%)'),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
        }
        return figure
    return {}


@app.callback(
    Output('profit-growth-graph', 'figure'),
    [Input('symbol-input', 'value')]
)
def update_profit_graph(symbol):
    _, profit_growth_rates = scrape_compounded_growth(symbol)
    if profit_growth_rates:
        # Convert growth rates to float and remove percentage signs
        profit_growth_rates = [float(rate.replace('%', '')) for rate in profit_growth_rates]

        # Create bar chart for profit growth
        figure = {
            'data': [go.Bar(
                y=['10 yrs', '5 yrs', '3 yrs', 'TTM'],
                x=profit_growth_rates,
                orientation='h'
            )],
            'layout': go.Layout(
                title='Profit Growth',
                yaxis=dict(title='Time Period'),
                xaxis=dict(title='Profit Growth (%)'),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
        }
        return figure
    return {}


if __name__ == '__main__':
    try:
        app.run_server(debug=True)
    except Exception as e:
        pass  # Handle the exception silently
