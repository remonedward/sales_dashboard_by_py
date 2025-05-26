import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
from dash.dcc import Download
from dash.dependencies import State
from functools import lru_cache
import dash_bootstrap_components as dbc


try:
    df = pd.read_csv('data.csv')
except FileNotFoundError:
    raise FileNotFoundError("ملف 'data.csv' غير موجود. تأكد من وجوده في المجلد المناسب.")
except pd.errors.EmptyDataError:
    raise ValueError("ملف 'data.csv' فارغ. يرجى التحقق من البيانات.")


required_columns = ['Month', 'Year', 'Region', 'Revenue', 'Units Sold', 'Profit']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"الأعمدة التالية مفقودة من ملف البيانات: {missing_columns}")


if df[required_columns].isnull().any().any():
    raise ValueError("يحتوي ملف البيانات على قيم مفقودة. يرجى التحقق من البيانات.")
if (df[['Revenue', 'Units Sold', 'Profit']] < 0).any().any():
    raise ValueError("يحتوي ملف البيانات على قيم سالبة في 'Revenue' أو 'Units Sold' أو 'Profit'. يرجى التحقق.")


@lru_cache(maxsize=128)
def get_monthly_sales():
    monthly_sales = df.groupby(['Year', 'Month'])['Revenue'].sum().reset_index()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June']
    monthly_sales['Month'] = pd.Categorical(monthly_sales['Month'], categories=month_order, ordered=True)
    return monthly_sales.sort_values(['Year', 'Month'])

# إنشاء التطبيق باستخدام Bootstrap لتحسين التصميم
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Sales Dashboard"


server = app.server


translations = {
    'ar': {
        'title': 'لوحة معلومات المبيعات',
        'select_year': 'اختر السنة:',
        'select_month': 'اختر الشهر:',
        'line_chart_title': 'اتجاه المبيعات الشهرية',
        'bar_chart_title': 'مبيعات شهر {month} حسب السنة والمنطقة',
        'pie_chart_title': 'توزيع المبيعات حسب المنطقة لشهر {month} في السنوات المختارة',
        'scatter_chart_title': 'الأرباح مقابل الوحدات المباعة لشهر {month} في السنوات المختارة',
        'revenue_label': 'إجمالي المبيعات',
        'month_label': 'الشهر',
        'year_label': 'السنة',
        'region_label': 'المنطقة',
        'profit_label': 'الربح',
        'units_sold_label': 'الوحدات المباعة',
        'data_table_title': 'بيانات المبيعات الخام',
        'export_line': 'تصدير الرسم الخطي',
        'export_bar': 'تصدير الرسم العمودي',
        'export_pie': 'تصدير الرسم الدائري',
        'export_scatter': 'تصدير الرسم المبعثر',
        'language_label': 'اللغة:'
    },
    'en': {
        'title': 'Sales Dashboard',
        'select_year': 'Select Year:',
        'select_month': 'Select Month:',
        'line_chart_title': 'Monthly Sales Trend',
        'bar_chart_title': 'Sales for {month} by Year and Region',
        'pie_chart_title': 'Sales Distribution by Region for {month} in Selected Years',
        'scatter_chart_title': 'Profit vs. Units Sold for {month} in Selected Years',
        'revenue_label': 'Total Sales',
        'month_label': 'Month',
        'year_label': 'Year',
        'region_label': 'Region',
        'profit_label': 'Profit',
        'units_sold_label': 'Units Sold',
        'data_table_title': 'Raw Sales Data',
        'export_line': 'Export Line Chart',
        'export_bar': 'Export Bar Chart',
        'export_pie': 'Export Pie Chart',
        'export_scatter': 'Export Scatter Chart',
        'language_label': 'Language:'
    }
}


app.layout = html.Div([
    
    html.Div([
        html.Label(id='language-label', style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='language-dropdown',
            options=[
                {'label': 'العربية', 'value': 'ar'},
                {'label': 'English', 'value': 'en'}
            ],
            value='ar',
            style={'width': '150px', 'display': 'inline-block'}
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),

    
    html.H1(id='dashboard-title', style={'textAlign': 'center', 'color': '#2c3e50'}),

    
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label(id='year-label'),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
                    value=[df['Year'].unique()[0]],
                    multi=True
                )
            ], width=5),
            dbc.Col([
                html.Label(id='month-label'),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[{'label': month, 'value': month} for month in df['Month'].unique()],
                    value=df['Month'].unique()[0]
                )
            ], width=5)
        ], justify='center', style={'marginBottom': '20px'})
    ]),

    
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='line-chart'),
                html.Button(id='export-line-button', className='btn btn-primary', style={'marginTop': '10px'}),
                dcc.Download(id='download-line')
            ], width=6),
            dbc.Col([
                dcc.Graph(id='bar-chart'),
                html.Button(id='export-bar-button', className='btn btn-primary', style={'marginTop': '10px'}),
                dcc.Download(id='download-bar')
            ], width=6)
        ], justify='center')
    ]),

    
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='pie-chart'),
                html.Button(id='export-pie-button', className='btn btn-primary', style={'marginTop': '10px'}),
                dcc.Download(id='download-pie')
            ], width=6),
            dbc.Col([
                dcc.Graph(id='scatter-chart'),
                html.Button(id='export-scatter-button', className='btn btn-primary', style={'marginTop': '10px'}),
                dcc.Download(id='download-scatter')
            ], width=6)
        ], justify='center')
    ]),

    
    html.H2(id='data-table-title', style={'textAlign': 'center', 'marginTop': '30px'}),
    dash_table.DataTable(
        id='data-table',
        columns=[
            {'name': 'Month', 'id': 'Month'},
            {'name': 'Year', 'id': 'Year'},
            {'name': 'Region', 'id': 'Region'},
            {'name': 'Revenue', 'id': 'Revenue'},
            {'name': 'Units Sold', 'id': 'Units Sold'},
            {'name': 'Profit', 'id': 'Profit'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '5px'},
        page_size=10
    )
], style={'padding': '20px', 'backgroundColor': '#f8f9fa'})


@app.callback(
    [
        Output('dashboard-title', 'children'),
        Output('year-label', 'children'),
        Output('month-label', 'children'),
        Output('language-label', 'children'),
        Output('export-line-button', 'children'),
        Output('export-bar-button', 'children'),
        Output('export-pie-button', 'children'),
        Output('export-scatter-button', 'children'),
        Output('data-table-title', 'children')
    ],
    Input('language-dropdown', 'value')
)
def update_language(language):
    return (
        translations[language]['title'],
        translations[language]['select_year'],
        translations[language]['select_month'],
        translations[language]['language_label'],
        translations[language]['export_line'],
        translations[language]['export_bar'],
        translations[language]['export_pie'],
        translations[language]['export_scatter'],
        translations[language]['data_table_title']
    )


@app.callback(
    Output('line-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('language-dropdown', 'value')
)
def update_line_chart(selected_years, language):
    if not isinstance(selected_years, list):
        selected_years = [selected_years]
    filtered_df = get_monthly_sales().query('Year in @selected_years')
    fig = px.line(
        filtered_df,
        x='Month',
        y='Revenue',
        color='Year',
        title=translations[language]['line_chart_title'],
        labels={
            'Revenue': translations[language]['revenue_label'],
            'Month': translations[language]['month_label'],
            'Year': translations[language]['year_label']
        },
        markers=True
    )
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        xaxis_title=translations[language]['month_label'],
        yaxis_title=translations[language]['revenue_label'],
        legend_title=translations[language]['year_label'],
        margin=dict(l=40, r=40, t=40, b=40),
        template='plotly_white'
    )
    return fig


@app.callback(
    Output('bar-chart', 'figure'),
    Input('month-dropdown', 'value'),
    Input('language-dropdown', 'value')
)
def update_bar_chart(selected_month, language):
    filtered_df = df[df['Month'] == selected_month]
    fig = px.bar(
        filtered_df,
        x='Year',
        y='Revenue',
        color='Region',
        title=translations[language]['bar_chart_title'].format(month=selected_month),
        labels={
            'Revenue': translations[language]['revenue_label'],
            'Year': translations[language]['year_label'],
            'Region': translations[language]['region_label']
        },
        barmode='group'
    )
    fig.update_layout(
        xaxis_title=translations[language]['year_label'],
        yaxis_title=translations[language]['revenue_label'],
        legend_title=translations[language]['region_label'],
        margin=dict(l=40, r=40, t=40, b=40),
        template='plotly_white'
    )
    return fig


@app.callback(
    Output('pie-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value'),
    Input('language-dropdown', 'value')
)
def update_pie_chart(selected_years, selected_month, language):
    if not isinstance(selected_years, list):
        selected_years = [selected_years]
    filtered_df = df[(df['Year'].isin(selected_years)) & (df['Month'] == selected_month)]
    fig = px.pie(
        filtered_df,
        names='Region',
        values='Revenue',
        title=translations[language]['pie_chart_title'].format(month=selected_month),
        hole=0.2
    )
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        legend_title=translations[language]['region_label'],
        margin=dict(l=40, r=40, t=40, b=40),
        template='plotly_white'
    )
    return fig


@app.callback(
    Output('scatter-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value'),
    Input('language-dropdown', 'value')
)
def update_scatter_chart(selected_years, selected_month, language):
    if not isinstance(selected_years, list):
        selected_years = [selected_years]
    filtered_df = df[(df['Year'].isin(selected_years)) & (df['Month'] == selected_month)]
    fig = px.scatter(
        filtered_df,
        x='Units Sold',
        y='Profit',
        color='Region',
        size='Revenue',
        title=translations[language]['scatter_chart_title'].format(month=selected_month),
        labels={
            'Units Sold': translations[language]['units_sold_label'],
            'Profit': translations[language]['profit_label'],
            'Region': translations[language]['region_label']
        }
    )
    fig.update_layout(
        xaxis_title=translations[language]['units_sold_label'],
        yaxis_title=translations[language]['profit_label'],
        legend_title=translations[language]['region_label'],
        margin=dict(l=40, r=40, t=40, b=40),
        template='plotly_white'
    )
    return fig


@app.callback(
    Output('data-table', 'data'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value')
)
def update_data_table(selected_years, selected_month):
    if not isinstance(selected_years, list):
        selected_years = [selected_years]
    filtered_df = df[(df['Year'].isin(selected_years)) & (df['Month'] == selected_month)]
    return filtered_df.to_dict('records')


@app.callback(
    Output('download-line', 'data'),
    Input('export-line-button', 'n_clicks'),
    prevent_initial_call=True
)
def export_line_chart(n_clicks):
    return dcc.send_file('line_chart.png')

@app.callback(
    Output('download-bar', 'data'),
    Input('export-bar-button', 'n_clicks'),
    prevent_initial_call=True
)
def export_bar_chart(n_clicks):
    return dcc.send_file('bar_chart.png')

@app.callback(
    Output('download-pie', 'data'),
    Input('export-pie-button', 'n_clicks'),
    prevent_initial_call=True
)
def export_pie_chart(n_clicks):
    return dcc.send_file('pie_chart.png')

@app.callback(
    Output('download-scatter', 'data'),
    Input('export-scatter-button', 'n_clicks'),
    prevent_initial_call=True
)
def export_scatter_chart(n_clicks):
    return dcc.send_file('scatter_chart.png')


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    # للنشر باستخدام Gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:8000 app:server