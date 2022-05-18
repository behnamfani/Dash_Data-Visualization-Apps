from dash import Dash, html, dcc, ALL, callback_context, dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.manifold import Isomap
from sklearn.decomposition import PCA
import warnings

warnings.simplefilter(action='ignore')


def Create_Dash(df, df_tsne, df_pca, df_isomap):
    app = Dash(__name__)
    app.layout = html.Div(children=[
        # Showing the scatter plots of t-SNE or PCA or ISOMAP dimensionality reduction techniques using Radio button
        html.H2(children='t-SNE/PCA/ISOMAP scatter plots',
                style={
                    'textAlign': 'center',
                    'color': '#107B8E'
                }
                ),

        html.Div(children=[
            dcc.RadioItems(['t-SNE', 'PCA', 'Isomap'], 't-SNE', id='which scatter plot', ),
        ], style={'margin-left': 50, 'padding': 5, 'border': '2px #850402 groove', 'width': 190, 'font-style': 'italic',
                  'font-weight': 'bold'}
        ),

        dcc.Graph(id='scatter plots', ),

        html.Hr(),

        # Choosing the axes for scatter plot of our data set
        html.H2(children='scatter plot with feature choices',
                style={
                    'textAlign': 'center',
                    'color': '#223048'
                }
                ),

        html.Div(children=[
            dcc.Dropdown(
                df.columns[:-1],
                'DYRK1A_N',
                id='feature1'
            ),

        ], style={'margin-left': 80, 'padding': 5, 'width': 180, 'font-style': 'oblique', 'background-color': '#7CF086',
                  'display': 'inline-block'}
        ),

        html.Div(children=[
            dcc.Dropdown(
                df.columns[:-1],
                'ITSN1_N',
                id='feature2'
            ),

        ], style={'margin-left': 50, 'padding': 5, 'width': 180, 'font-style': 'oblique',
                  'background-color': '#7CF086', 'display': 'inline-block'}
        ),
        dbc.Button(id='Add-val', n_clicks=0, children='Add', style={'margin-left': 1400, 'padding': 20,
                                                                    'font-style': 'oblique',
                                                                    'color': 'white',
                                                                    'background-color': 'blue',
                                                                    'display': 'inline-block',
                                                                    'title': 'Add new scatter plot'},
                   ),

        dcc.Graph(id='scatter plot', ),

        html.Hr(),

        # Add scatter plot whenever a user wants using Add burron
        html.H2(children='Adding scatters',
                style={
                    'textAlign': 'center',
                    'color': '#223048'
                }
                ),

        html.Div(id='flexible scatter', children=[
        ]),

        dbc.Button(id='Delete-val', n_clicks=0, children='Delete',
                   style={'margin-left': 1400,
                          'padding': 20,
                          'font-style': 'oblique',
                          'color': 'white',
                          'background-color': 'black',
                          'title': 'Delete selected scatter plots'
                          })

    ])

    @app.callback(
        Output('scatter plots', 'figure'),
        Output('scatter plot', 'figure'),
        Input('which scatter plot', 'value'),
        Input('feature1', 'value'),
        Input('feature2', 'value'),
    )
    def update(f, f1, f2):
        fig = None
        # Which dimensionality reduction plot to draw
        if f == 't-SNE':
            fig_tsne = px.scatter(df_tsne, x="comp-1", y="comp-2", color="class",
                                  color_discrete_sequence=px.colors.qualitative.Light24)
            fig = fig_tsne

        elif f == 'PCA':
            fig_pca = px.scatter(df_pca, x="comp-1", y="comp-2", color="class",
                                 color_discrete_sequence=px.colors.qualitative.Bold)
            fig = fig_pca
        else:
            fig_isomap = px.scatter(df_isomap, x="comp-1", y="comp-2", color="class",
                                    color_discrete_sequence=px.colors.qualitative.Vivid)
            fig = fig_isomap

        # Draw scatter plot of dataset with option of choosing the features
        fig2 = px.scatter(df, x=f1, y=f2, color="class", color_discrete_sequence=['cyan', 'gold'])

        return fig, fig2

    @app.callback(
        Output('flexible scatter', 'children'),
        Input('Add-val', 'n_clicks'),
        Input('Delete-val', 'n_clicks'),
        State('flexible scatter', 'children'),
        State('feature1', 'value'),
        State('feature2', 'value'),
        State({'type': 'Checklist', 'index': ALL}, 'value')
    )
    def Add_Scatter(add_btn, del_btn, children, f1, f2, value):
        # Add scatter plot (+ check button) if states are triggered by Add button
        if 'Add' in callback_context.triggered[0]['prop_id']:
            fig3 = px.scatter(df, x=f1, y=f2, color="class", color_discrete_sequence=['green', 'grey'])
            x = html.Div(children=[dcc.Checklist(options=[{"label": "", "value": add_btn}], id={'type': 'Checklist',
                                                                                                'index': add_btn},
                                                 style={'margin-left': 80, 'padding': 8}),
                                   dcc.Graph(figure=fig3),
                                   ],
                         id=str(add_btn),
                         style={'margin': 10, 'width': 440, 'display': 'inline-block'})
            children.append(x)

        # Delete scatter plot (+ check button) that are checked if states are triggered by Delete button and
        if 'Delete' in callback_context.triggered[0]['prop_id'] and add_btn > 0:
            for val in value:
                if val is not None and len(i) > 0:
                    for delete, j in enumerate(children):
                        if val[0] == int(j['props']['id']):
                            children.pop(delete)

        return children

    return app


if __name__ == '__main__':
    # Read and pre-process the data set --------------------
    df = pd.read_excel(
        'D:/Python/CODE/Dash_App/Data_Cortex_Nuclear.xls')
    df = df.loc[(df['class'] == 'c-CS-s') | (df['class'] == 't-CS-s')]
    df = df.drop(columns=['MouseID', 'Genotype', 'Treatment', 'Behavior'])
    df.reset_index(drop=True, inplace=True)

    for i in df.columns:
        if df[i].isnull().values.any():
            df[i] = df[i].fillna(df[i].mean())

    # print('DataFrame: \n', df.head())

    # t-SNE dimensionality reduction --------------------------
    tsne = TSNE(n_components=2)
    tsne_transform = tsne.fit_transform(df.iloc[:, :-1])
    df_tsne = pd.DataFrame({"comp-1": tsne_transform[:, 0], "comp-2": tsne_transform[:, 1], "class": df['class']})
    # print('t-SNE DataFrame: \n', df_tsne.head())

    # PCA dimensionality reduction ---------------------------
    pca = PCA(n_components=2)
    pca_transform = pca.fit_transform(df.iloc[:, :-1])
    df_pca = pd.DataFrame({"comp-1": pca_transform[:, 0], "comp-2": pca_transform[:, 1], "class": df['class']})
    # print('PCA DataFrame: \n', df_pca.head())

    # ISOMAP dimensionality reduction ------------------------
    isomap = Isomap(n_components=2)
    isomap_transform = isomap.fit_transform(df.iloc[:, :-1])
    df_isomap = pd.DataFrame({"comp-1": isomap_transform[:, 0], "comp-2": isomap_transform[:, 1], "class": df['class']})
    # print('isomap DataFrame: \n', df_isomap.head())

    # Create Dash App
    app = Create_Dash(df, df_tsne, df_pca, df_isomap)
    app.run_server(debug=True)
