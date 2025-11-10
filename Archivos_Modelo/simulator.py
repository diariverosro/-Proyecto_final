import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests  # Para llamar a tu API
import pandas as pd  # Lo necesitamos para leer el CSV y obtener los valores únicos

# --- 1. Carga el CSV para obtener las opciones de los menús ---
try:
    # Asegúrate que el CSV esté en la misma carpeta (Version_1)
    df = pd.read_csv('Sleep_health_and_lifestyle_dataset(in).csv')
    
    # Obtenemos las listas de valores únicos
    gender_options = sorted(df['Gender'].unique())
    occupation_options = sorted(df['Occupation'].unique())
    bmi_options = sorted(df['BMI Category'].unique())
    # Para Sleep Disorder, necesitamos añadir la opción "None" que creamos
    disorder_options = sorted(df['Sleep Disorder'].fillna('No Sleep Disorder').unique())
    
    # Usamos la primera fila del dataset como nuestros valores iniciales
    initial_values = df.iloc[0]

except FileNotFoundError:
    print("ADVERTENCIA: 'Sleep_health_and_lifestyle_dataset(in).csv' no encontrado.")
    print("Usando valores manuales. El simulador podría funcionar, pero los menús estarán incompletos.")
    # Fallback por si no encuentra el archivo
    gender_options = ['Male', 'Female']
    occupation_options = ['Software Engineer', 'Doctor', 'Nurse']
    bmi_options = ['Overweight', 'Normal', 'Obese']
    disorder_options = ['No Sleep Disorder', 'Sleep Apnea', 'Insomnia']
    initial_values = {
        "Gender": "Male", "Age": 27, "Occupation": "Software Engineer", 
        "Sleep Duration": 6.1, "Physical Activity Level": 42, "Stress Level": 6, 
        "BMI Category": "Overweight", "Blood Pressure": "126/83", "Heart Rate": 77, 
        "Daily Steps": 4200, "Sleep Disorder": None
    }

app = dash.Dash(__name__)

# --- 2. Define la Interfaz (Actualizada con Dropdowns y Valores) ---
app.layout = html.Div(style={'padding': '20px'}, children=[
    html.H1("Simulador de Calidad de Sueño"),
    html.P("Ajusta los valores para simular la calidad de sueño de un perfil."),

    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '15px'}, children=[
        
        # --- Variables Categóricas (Menús Desplegables) ---
        html.Div([
            html.Label("Género"),
            dcc.Dropdown(
                id='gender-input',
                options=[{'label': i, 'value': i} for i in gender_options],
                value=initial_values['Gender'] # Valor inicial
            )
        ]),
        
        html.Div([
            html.Label("Ocupación"),
            dcc.Dropdown(
                id='occupation-input',
                options=[{'label': i, 'value': i} for i in occupation_options],
                value=initial_values['Occupation'] # Valor inicial
            )
        ]),

        html.Div([
            html.Label("Categoría BMI"),
            dcc.Dropdown(
                id='bmi-input',
                options=[{'label': i, 'value': i} for i in bmi_options],
                value=initial_values['BMI Category'] # Valor inicial
            )
        ]),

        html.Div([
            html.Label("Desorden de Sueño (Opcional)"),
            dcc.Dropdown(
                id='disorder-input',
                options=[{'label': i, 'value': i} for i in disorder_options] + [{'label': 'Nulo/Vacío', 'value': 'None'}],
                value='None' # Empezamos con Nulo
            )
        ]),

        # --- Variables Numéricas/Texto (Campos con valor inicial) ---
        html.Div([
            html.Label("Edad"),
            dcc.Input(id='age-input', type='number', value=initial_values['Age'], style={'width': '100%'})
        ]),
        
        html.Div([
            html.Label("Duración de Sueño (hrs)"),
            dcc.Input(id='sleep-duration-input', type='number', value=initial_values['Sleep Duration'], style={'width': '100%'})
        ]),
        
        html.Div([
            html.Label("Nivel Actividad Física (min/día)"),
            dcc.Input(id='activity-input', type='number', value=initial_values['Physical Activity Level'], style={'width': '100%'})
        ]),
        
        html.Div([
            html.Label("Nivel de Estrés (1-10)"),
            dcc.Input(id='stress-input', type='number', value=initial_values['Stress Level'], style={'width': '100%'})
        ]),

        html.Div([
            html.Label("Presión Arterial (sis/dia)"),
            dcc.Input(id='bp-input', type='text', value=initial_values['Blood Pressure'], style={'width': '100%'})
        ]),
        
        html.Div([
            html.Label("Ritmo Cardíaco (ppm)"),
            dcc.Input(id='hr-input', type='number', value=initial_values['Heart Rate'], style={'width': '100%'})
        ]),
        
        html.Div([
            html.Label("Pasos Diarios"),
            dcc.Input(id='steps-input', type='number', value=initial_values['Daily Steps'], style={'width': '100%'})
        ]),
    ]),
    
    html.Br(),
    # Botón para ejecutar la simulación
    html.Button('Simular Predicción', id='predict-button', n_clicks=0, style={'fontSize': '18px', 'padding': '10px'}),
    html.Hr(),
    
    # Sección de resultados
    html.H2("Resultado de la Simulación:"),
    html.Div(id='prediction-output', style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#007BFF'})
])

# --- 3. Define la Interactividad (El Callback) ---
# ¡Esta parte no necesita casi ningún cambio!
# El callback recoge los valores de los componentes por su 'id',
# no le importa si es un 'dcc.Input' o un 'dcc.Dropdown'.
@app.callback(
    Output('prediction-output', 'children'),
    Input('predict-button', 'n_clicks'),
    [
        # Recoge el valor de CADA uno de tus controles
        State('gender-input', 'value'),
        State('age-input', 'value'),
        State('occupation-input', 'value'),
        State('sleep-duration-input', 'value'),
        State('activity-input', 'value'),
        State('stress-input', 'value'),
        State('bmi-input', 'value'),
        State('bp-input', 'value'),
        State('hr-input', 'value'),
        State('steps-input', 'value'),
        State('disorder-input', 'value')
    ]
)
def update_prediction(n_clicks, gender, age, occupation, sleep_dur, activity, stress, bmi, bp, hr, steps, disorder):
    if n_clicks == 0:
        return "Ajuste los valores y presione 'Simular'."

    # 3. Construye el JSON para tu API (¡los nombres deben tener ESPACIOS!)
    api_payload = {
        "Gender": gender,
        "Age": age,
        "Occupation": occupation,
        "Sleep Duration": sleep_dur,
        "Physical Activity Level": activity,
        "Stress Level": stress,
        "BMI Category": bmi,
        "Blood Pressure": bp,
        "Heart Rate": hr,
        "Daily Steps": steps,
        # Maneja la opción 'None' que pusimos en el dropdown
        "Sleep Disorder": None if disorder in [None, "None", ""] else disorder
    }

    try:
        # 4. LLAMA A TU API DE FASTAPI (que corre en el puerto 8000)
        api_url = "http://localhost:8000/predict"
        response = requests.post(api_url, json=api_payload)

        if response.status_code == 200:
            # 5. Muestra el resultado
            prediction = response.json()['predicted_quality_of_sleep']
            return f"Calidad de Sueño Predicha: {prediction} (sobre 10)"
        else:
            # Muestra el error de validación de Pydantic
            return f"Error de la API: {response.text}"
            
    except Exception as e:
        return f"Error de conexión: No se pudo conectar a la API en {api_url}. ¿Está corriendo? {str(e)}"

# --- 4. Corre el servidor de Dash ---
if __name__ == '__main__':
    # Usamos app.run (como corregimos antes)
    app.run(debug=True, host='0.0.0.0', port=8050)