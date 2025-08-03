from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine.

    Parâmetros:
        lat1, lon1: latitude e longitude do ponto 1
        lat2, lon2: latitude e longitude do ponto 2

    Retorna:
        Distância em quilômetros (float)
    """
    R = 6371.0  # Raio da Terra em km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
