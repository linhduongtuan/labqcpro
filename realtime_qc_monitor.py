"""
Real-Time Laboratory QC Monitoring Dashboard
Uses Plotly Dash for interactive web-based monitoring
Simulates real-time data streaming and automatic Westgard rule checking
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque
import threading
import time
from lab_qc_analysis import LabQCAnalysis

# Initialize
qc = LabQCAnalysis(seed=None)  # Random seed for varying data

# Global data storage (thread-safe)
max_points = 100
data_storage = {
    'creatinine': {
        'times': deque(maxlen=max_points),
        'values': deque(maxlen=max_points),
        'violations': deque(maxlen=50)
    },
    'urea': {
        'times': deque(maxlen=max_points),
        'values': deque(maxlen=max_points),
        'violations': deque(maxlen=50)
    }
}

# Statistics storage
stats_storage = {
    'creatinine': {'mean': 0, 'sd': 0, 'cv': 0, 'bias': 0, 'sigma': 0},
    'urea': {'mean': 0, 'sd': 0, 'cv': 0, 'bias': 0, 'sigma': 0}
}

# Alert flags
alert_flags = {
    'creatinine': {'status': 'OK', 'message': '', 'count': 0},
    'urea': {'status': 'OK', 'message': '', 'count': 0}
}

def generate_new_measurement(analyte, add_shift=False, add_outlier=False):
    """Generate a new simulated measurement"""
    params = qc.parameters[analyte]
    
    # Base value
    value = np.random.normal(params['mean'], params['std'])
    
    # Add systematic shift if requested
    if add_shift:
        value += params['std'] * 1.5
    
    # Add outlier if requested
    if add_outlier:
        value += np.random.choice([-1, 1]) * params['std'] * 3.5
    
    return value


def check_westgard_violation(analyte, new_value):
    """Check if new value violates Westgard rules"""
    params = qc.parameters[analyte]
    mean = params['mean']
    std = params['std']
    
    storage = data_storage[analyte]
    values = list(storage['values'])
    
    if len(values) < 2:
        return None
    
    z_score = (new_value - mean) / std
    
    # Rule 1-3s
    if abs(z_score) > 3:
        return {
            'time': datetime.now(),
            'value': new_value,
            'rule': '1-3s',
            'severity': 'CRITICAL',
            'message': 'One control exceeds ±3 SD'
        }
    
    # Rule 2-2s
    if len(values) >= 1:
        z_prev = (values[-1] - mean) / std
        if abs(z_score) > 2 and abs(z_prev) > 2:
            if np.sign(z_score) == np.sign(z_prev):
                return {
                    'time': datetime.now(),
                    'value': new_value,
                    'rule': '2-2s',
                    'severity': 'CRITICAL',
                    'message': 'Two consecutive controls exceed ±2 SD'
                }
    
    # Rule R-4s
    if len(values) >= 1:
        range_val = abs(new_value - values[-1])
        if range_val > 4 * std:
            return {
                'time': datetime.now(),
                'value': new_value,
                'rule': 'R-4s',
                'severity': 'CRITICAL',
                'message': 'Range exceeds 4 SD'
            }
    
    # Rule 4-1s
    if len(values) >= 3:
        last_4_z = [z_score] + [(values[i] - mean) / std for i in range(-3, 0)]
        if all(z > 1 for z in last_4_z) or all(z < -1 for z in last_4_z):
            return {
                'time': datetime.now(),
                'value': new_value,
                'rule': '4-1s',
                'severity': 'WARNING',
                'message': 'Four consecutive controls exceed ±1 SD'
            }
    
    # Rule 10-x
    if len(values) >= 9:
        last_10 = [new_value] + values[-9:]
        if all(val > mean for val in last_10) or all(val < mean for val in last_10):
            return {
                'time': datetime.now(),
                'value': new_value,
                'rule': '10-x',
                'severity': 'CRITICAL',
                'message': '10 consecutive controls on same side of mean'
            }
    
    return None


def update_statistics(analyte):
    """Calculate current statistics"""
    storage = data_storage[analyte]
    values = list(storage['values'])
    
    if len(values) < 3:
        return
    
    params = qc.parameters[analyte]
    values_array = np.array(values)
    
    mean = np.mean(values_array)
    sd = np.std(values_array, ddof=1)
    cv = (sd / mean) * 100 if mean != 0 else 0
    bias = ((mean - params['mean']) / params['mean']) * 100
    
    # Calculate Sigma
    tea_pct = params['tea'] * 100
    if cv > 0:
        sigma = (tea_pct - abs(bias)) / cv
    else:
        sigma = 0
    
    stats_storage[analyte] = {
        'mean': mean,
        'sd': sd,
        'cv': cv,
        'bias': bias,
        'sigma': sigma,
        'n': len(values)
    }


def data_generator():
    """Background thread to generate new data points"""
    simulation_scenarios = {
        'normal': {'shift': False, 'outlier': False, 'weight': 0.7},
        'shift': {'shift': True, 'outlier': False, 'weight': 0.15},
        'outlier': {'shift': False, 'outlier': True, 'weight': 0.15}
    }
    
    while True:
        # Choose scenario
        scenario_type = np.random.choice(
            list(simulation_scenarios.keys()),
            p=[s['weight'] for s in simulation_scenarios.values()]
        )
        scenario = simulation_scenarios[scenario_type]
        
        # Generate measurements for both analytes
        for analyte in ['creatinine', 'urea']:
            new_value = generate_new_measurement(
                analyte, 
                add_shift=scenario['shift'],
                add_outlier=scenario['outlier']
            )
            
            current_time = datetime.now()
            
            # Store data
            data_storage[analyte]['times'].append(current_time)
            data_storage[analyte]['values'].append(new_value)
            
            # Check for violations
            violation = check_westgard_violation(analyte, new_value)
            if violation:
                data_storage[analyte]['violations'].append(violation)
                alert_flags[analyte]['status'] = 'ALERT'
                alert_flags[analyte]['message'] = violation['message']
                alert_flags[analyte]['count'] += 1
            else:
                if alert_flags[analyte]['count'] == 0:
                    alert_flags[analyte]['status'] = 'OK'
                    alert_flags[analyte]['message'] = 'All controls within limits'
            
            # Update statistics
            update_statistics(analyte)
        
        # Wait before next measurement (simulate real-time)
        time.sleep(2)  # New measurement every 2 seconds


# Initialize Dash app
app = dash.Dash(__name__, update_title='QC Monitor...')
app.title = 'Laboratory QC Real-Time Monitor'

# App layout
app.layout = html.Div([
    html.Div([
        html.H1('🔬 Laboratory QC Real-Time Monitoring Dashboard', 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.H4(id='live-update-time', 
                style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': 0}),
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
    
    # Alert Banners
    html.Div([
        html.Div(id='creatinine-alert', style={'flex': 1, 'marginRight': '10px'}),
        html.Div(id='urea-alert', style={'flex': 1, 'marginLeft': '10px'}),
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Main Charts
    html.Div([
        dcc.Graph(id='creatinine-chart', style={'height': '400px'}),
    ], style={'marginBottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='urea-chart', style={'height': '400px'}),
    ], style={'marginBottom': '20px'}),
    
    # Statistics Dashboard
    html.Div([
        html.H3('📊 Current Statistics', style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Div([
            html.Div(id='creatinine-stats', style={'flex': 1, 'marginRight': '10px'}),
            html.Div(id='urea-stats', style={'flex': 1, 'marginLeft': '10px'}),
        ], style={'display': 'flex'}),
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
    
    # Violations Log
    html.Div([
        html.H3('⚠️ Recent Violations', style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Div(id='violations-log', style={'maxHeight': '300px', 'overflowY': 'auto'}),
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px'}),
    
    # Auto-update interval
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every 1 second
        n_intervals=0
    ),
    
    # Control buttons
    html.Div([
        html.Button('🔄 Reset Data', id='reset-button', n_clicks=0,
                   style={'padding': '10px 20px', 'fontSize': '16px', 'marginRight': '10px',
                         'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
                         'borderRadius': '5px', 'cursor': 'pointer'}),
        html.Button('📊 Export CSV', id='export-button', n_clicks=0,
                   style={'padding': '10px 20px', 'fontSize': '16px',
                         'backgroundColor': '#2ecc71', 'color': 'white', 'border': 'none',
                         'borderRadius': '5px', 'cursor': 'pointer'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),
    
    dcc.Download(id='download-data'),
    
], style={'padding': '20px', 'backgroundColor': '#f5f5f5', 'fontFamily': 'Arial, sans-serif'})


@app.callback(
    Output('live-update-time', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_time(n):
    return f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@app.callback(
    Output('creatinine-alert', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_creatinine_alert(n):
    alert = alert_flags['creatinine']
    
    if alert['status'] == 'ALERT':
        style = {
            'backgroundColor': '#e74c3c',
            'color': 'white',
            'padding': '15px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'fontWeight': 'bold'
        }
        return html.Div([
            html.H4('🚨 CREATININE ALERT', style={'margin': '0 0 10px 0'}),
            html.P(alert['message'], style={'margin': 0}),
            html.P(f"Total Violations: {alert['count']}", style={'margin': '10px 0 0 0', 'fontSize': '14px'})
        ], style=style)
    else:
        style = {
            'backgroundColor': '#2ecc71',
            'color': 'white',
            'padding': '15px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'fontWeight': 'bold'
        }
        return html.Div([
            html.H4('✅ CREATININE OK', style={'margin': '0 0 10px 0'}),
            html.P('All controls within limits', style={'margin': 0})
        ], style=style)


@app.callback(
    Output('urea-alert', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_urea_alert(n):
    alert = alert_flags['urea']
    
    if alert['status'] == 'ALERT':
        style = {
            'backgroundColor': '#e74c3c',
            'color': 'white',
            'padding': '15px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'fontWeight': 'bold'
        }
        return html.Div([
            html.H4('🚨 UREA ALERT', style={'margin': '0 0 10px 0'}),
            html.P(alert['message'], style={'margin': 0}),
            html.P(f"Total Violations: {alert['count']}", style={'margin': '10px 0 0 0', 'fontSize': '14px'})
        ], style=style)
    else:
        style = {
            'backgroundColor': '#2ecc71',
            'color': 'white',
            'padding': '15px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'fontWeight': 'bold'
        }
        return html.Div([
            html.H4('✅ UREA OK', style={'margin': '0 0 10px 0'}),
            html.P('All controls within limits', style={'margin': 0})
        ], style=style)


@app.callback(
    Output('creatinine-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_creatinine_chart(n):
    storage = data_storage['creatinine']
    params = qc.parameters['creatinine']
    
    times = list(storage['times'])
    values = list(storage['values'])
    
    if len(times) == 0:
        times = [datetime.now()]
        values = [params['mean']]
    
    mean = params['mean']
    std = params['std']
    
    fig = go.Figure()
    
    # Data points
    fig.add_trace(go.Scatter(
        x=times, y=values,
        mode='lines+markers',
        name='Measurements',
        line=dict(color='#3498db', width=2),
        marker=dict(size=8)
    ))
    
    # Control limits
    fig.add_hline(y=mean, line_dash="solid", line_color="green", line_width=2,
                  annotation_text="Mean", annotation_position="right")
    fig.add_hline(y=mean + std, line_dash="dash", line_color="yellow", line_width=1.5,
                  annotation_text="+1 SD", annotation_position="right")
    fig.add_hline(y=mean - std, line_dash="dash", line_color="yellow", line_width=1.5)
    fig.add_hline(y=mean + 2*std, line_dash="dash", line_color="orange", line_width=1.5,
                  annotation_text="+2 SD", annotation_position="right")
    fig.add_hline(y=mean - 2*std, line_dash="dash", line_color="orange", line_width=1.5)
    fig.add_hline(y=mean + 3*std, line_dash="solid", line_color="red", line_width=2,
                  annotation_text="+3 SD", annotation_position="right")
    fig.add_hline(y=mean - 3*std, line_dash="solid", line_color="red", line_width=2)
    
    fig.update_layout(
        title='Creatinine - Real-Time Levey-Jennings Chart',
        xaxis_title='Time',
        yaxis_title=f'Creatinine ({params["unit"]})',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig


@app.callback(
    Output('urea-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_urea_chart(n):
    storage = data_storage['urea']
    params = qc.parameters['urea']
    
    times = list(storage['times'])
    values = list(storage['values'])
    
    if len(times) == 0:
        times = [datetime.now()]
        values = [params['mean']]
    
    mean = params['mean']
    std = params['std']
    
    fig = go.Figure()
    
    # Data points
    fig.add_trace(go.Scatter(
        x=times, y=values,
        mode='lines+markers',
        name='Measurements',
        line=dict(color='#9b59b6', width=2),
        marker=dict(size=8)
    ))
    
    # Control limits
    fig.add_hline(y=mean, line_dash="solid", line_color="green", line_width=2,
                  annotation_text="Mean", annotation_position="right")
    fig.add_hline(y=mean + std, line_dash="dash", line_color="yellow", line_width=1.5,
                  annotation_text="+1 SD", annotation_position="right")
    fig.add_hline(y=mean - std, line_dash="dash", line_color="yellow", line_width=1.5)
    fig.add_hline(y=mean + 2*std, line_dash="dash", line_color="orange", line_width=1.5,
                  annotation_text="+2 SD", annotation_position="right")
    fig.add_hline(y=mean - 2*std, line_dash="dash", line_color="orange", line_width=1.5)
    fig.add_hline(y=mean + 3*std, line_dash="solid", line_color="red", line_width=2,
                  annotation_text="+3 SD", annotation_position="right")
    fig.add_hline(y=mean - 3*std, line_dash="solid", line_color="red", line_width=2)
    
    fig.update_layout(
        title='Urea - Real-Time Levey-Jennings Chart',
        xaxis_title='Time',
        yaxis_title=f'Urea ({params["unit"]})',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig


@app.callback(
    Output('creatinine-stats', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_creatinine_stats(n):
    stats = stats_storage['creatinine']
    params = qc.parameters['creatinine']
    
    # Determine sigma color
    sigma_val = stats.get('sigma', 0)
    if sigma_val >= 6:
        sigma_color = '#2ecc71'
        sigma_text = 'World Class'
    elif sigma_val >= 5:
        sigma_color = '#27ae60'
        sigma_text = 'Excellent'
    elif sigma_val >= 4:
        sigma_color = '#f39c12'
        sigma_text = 'Good'
    elif sigma_val >= 3:
        sigma_color = '#e67e22'
        sigma_text = 'Marginal'
    else:
        sigma_color = '#e74c3c'
        sigma_text = 'Poor'
    
    return html.Div([
        html.H4('Creatinine Statistics', style={'color': '#2c3e50', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
        html.Table([
            html.Tr([html.Td('Target Mean:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{params['mean']:.4f} {params['unit']}")]),
            html.Tr([html.Td('Current Mean:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('mean', 0):.4f} {params['unit']}")]),
            html.Tr([html.Td('SD:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('sd', 0):.4f}")]),
            html.Tr([html.Td('CV:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('cv', 0):.2f}%")]),
            html.Tr([html.Td('Bias:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('bias', 0):.2f}%")]),
            html.Tr([html.Td('Sigma:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{sigma_val:.2f}", style={'color': sigma_color, 'fontWeight': 'bold'})]),
            html.Tr([html.Td('Quality:', style={'fontWeight': 'bold'}), 
                    html.Td(sigma_text, style={'color': sigma_color, 'fontWeight': 'bold'})]),
            html.Tr([html.Td('N:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('n', 0)}")]),
        ], style={'width': '100%', 'fontSize': '14px'})
    ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px'})


@app.callback(
    Output('urea-stats', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_urea_stats(n):
    stats = stats_storage['urea']
    params = qc.parameters['urea']
    
    # Determine sigma color
    sigma_val = stats.get('sigma', 0)
    if sigma_val >= 6:
        sigma_color = '#2ecc71'
        sigma_text = 'World Class'
    elif sigma_val >= 5:
        sigma_color = '#27ae60'
        sigma_text = 'Excellent'
    elif sigma_val >= 4:
        sigma_color = '#f39c12'
        sigma_text = 'Good'
    elif sigma_val >= 3:
        sigma_color = '#e67e22'
        sigma_text = 'Marginal'
    else:
        sigma_color = '#e74c3c'
        sigma_text = 'Poor'
    
    return html.Div([
        html.H4('Urea Statistics', style={'color': '#2c3e50', 'borderBottom': '2px solid #9b59b6', 'paddingBottom': '10px'}),
        html.Table([
            html.Tr([html.Td('Target Mean:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{params['mean']:.4f} {params['unit']}")]),
            html.Tr([html.Td('Current Mean:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('mean', 0):.4f} {params['unit']}")]),
            html.Tr([html.Td('SD:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('sd', 0):.4f}")]),
            html.Tr([html.Td('CV:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('cv', 0):.2f}%")]),
            html.Tr([html.Td('Bias:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('bias', 0):.2f}%")]),
            html.Tr([html.Td('Sigma:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{sigma_val:.2f}", style={'color': sigma_color, 'fontWeight': 'bold'})]),
            html.Tr([html.Td('Quality:', style={'fontWeight': 'bold'}), 
                    html.Td(sigma_text, style={'color': sigma_color, 'fontWeight': 'bold'})]),
            html.Tr([html.Td('N:', style={'fontWeight': 'bold'}), 
                    html.Td(f"{stats.get('n', 0)}")]),
        ], style={'width': '100%', 'fontSize': '14px'})
    ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px'})


@app.callback(
    Output('violations-log', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_violations_log(n):
    all_violations = []
    
    for analyte in ['creatinine', 'urea']:
        violations = list(data_storage[analyte]['violations'])
        for v in violations:
            all_violations.append({
                'analyte': analyte,
                'time': v['time'],
                'rule': v['rule'],
                'severity': v['severity'],
                'message': v['message'],
                'value': v['value']
            })
    
    # Sort by time (most recent first)
    all_violations.sort(key=lambda x: x['time'], reverse=True)
    
    if len(all_violations) == 0:
        return html.Div('No violations detected', 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'})
    
    violation_items = []
    for v in all_violations[:10]:  # Show last 10
        severity_color = '#e74c3c' if v['severity'] == 'CRITICAL' else '#f39c12'
        
        violation_items.append(
            html.Div([
                html.Div([
                    html.Span(v['analyte'].upper(), 
                             style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    html.Span(v['rule'], 
                             style={'backgroundColor': severity_color, 'color': 'white',
                                   'padding': '2px 8px', 'borderRadius': '3px', 'fontSize': '12px',
                                   'marginRight': '10px'}),
                    html.Span(v['time'].strftime('%H:%M:%S'), 
                             style={'color': '#7f8c8d', 'fontSize': '12px'})
                ]),
                html.Div(v['message'], style={'marginTop': '5px', 'fontSize': '14px'}),
                html.Div(f"Value: {v['value']:.4f}", 
                        style={'marginTop': '5px', 'fontSize': '12px', 'color': '#7f8c8d'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px',
                     'marginBottom': '10px', 'borderLeft': f'4px solid {severity_color}'})
        )
    
    return html.Div(violation_items)


@app.callback(
    Output('download-data', 'data'),
    Input('export-button', 'n_clicks'),
    prevent_initial_call=True
)
def export_data(n_clicks):
    # Combine all data
    export_data = []
    
    for analyte in ['creatinine', 'urea']:
        times = list(data_storage[analyte]['times'])
        values = list(data_storage[analyte]['values'])
        
        for t, v in zip(times, values):
            export_data.append({
                'Analyte': analyte,
                'Time': t.strftime('%Y-%m-%d %H:%M:%S'),
                'Value': v,
                'Mean': stats_storage[analyte].get('mean', 0),
                'SD': stats_storage[analyte].get('sd', 0),
                'CV': stats_storage[analyte].get('cv', 0),
                'Bias': stats_storage[analyte].get('bias', 0),
                'Sigma': stats_storage[analyte].get('sigma', 0)
            })
    
    df = pd.DataFrame(export_data)
    return dcc.send_data_frame(df.to_csv, f"qc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)


@app.callback(
    Output('interval-component', 'n_intervals'),
    Input('reset-button', 'n_clicks'),
    State('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def reset_data(n_clicks, current_interval):
    # Clear all data
    for analyte in ['creatinine', 'urea']:
        data_storage[analyte]['times'].clear()
        data_storage[analyte]['values'].clear()
        data_storage[analyte]['violations'].clear()
        stats_storage[analyte] = {'mean': 0, 'sd': 0, 'cv': 0, 'bias': 0, 'sigma': 0}
        alert_flags[analyte] = {'status': 'OK', 'message': '', 'count': 0}
    
    return 0


if __name__ == '__main__':
    # Start background data generation thread
    data_thread = threading.Thread(target=data_generator, daemon=True)
    data_thread.start()
    
    print("\n" + "="*80)
    print("🔬 LABORATORY QC REAL-TIME MONITORING DASHBOARD")
    print("="*80)
    print("\n📊 Starting real-time monitoring system...")
    print("🌐 Open your browser and navigate to: http://127.0.0.1:8050")
    print("\n✨ Features:")
    print("   • Live Levey-Jennings charts for Creatinine & Urea")
    print("   • Automatic Westgard rule checking")
    print("   • Real-time statistics (Mean, SD, CV, Bias, Sigma)")
    print("   • Alert notifications for violations")
    print("   • Data export to CSV")
    print("   • Auto-refresh every 1 second")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    # Run the Dash app
    app.run(debug=False, host='0.0.0.0', port=8050)
