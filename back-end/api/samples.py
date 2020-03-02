TRAINED_MODELS = {
  'XGB001': {"model-type": "XGBoost", "learning-rate": 0.6, "max-depth": 11, "train-split": 80, "validation-split": 20, "rmse": 15000},
  'RF001': {"model-type": "RandomForest", "learning-rate": 0.5, "max-depth": 8, "train-split": 75, "validation-split": 25, "rmse": 17500},
  'XGB002': {"model-type": "XGBoost", "learning-rate": 0.5, "max-depth": 8, "train-split": 70, "validation-split": 30, "rmse": 20000},
  'XGB003': {"model-type": "XGBoost", "learning-rate": 0.4, "max-depth": 5, "train-split": 80, "validation-split": 20, "rmse": 12500},
  'LRG001': {"model-type": "LinearRegression", "learning-rate": 0.5, "max-depth": 8, "train-split": 80, "validation-split": 20, "rmse": 10000}
}

WEATHER_FORECAST = {
  '00:00' : {"wind": 5, "temperature": 289, "cloud-cover": 13},
  '01:00' : {"wind": 6, "temperature": 283, "cloud-cover": 24},
  '02:00' : {"wind": 7, "temperature": 295, "cloud-cover": 51},
  '03:00' : {"wind": 5, "temperature": 293, "cloud-cover": 18},
  '04:00' : {"wind": 6, "temperature": 279, "cloud-cover": 1},
  '05:00' : {"wind": 5, "temperature": 301, "cloud-cover": 87},
  '06:00' : {"wind": 4, "temperature": 299, "cloud-cover": 35},
  '07:00' : {"wind": 3, "temperature": 286, "cloud-cover": 53},
  '08:00' : {"wind": 2, "temperature": 276, "cloud-cover": 2},
  '09:00' : {"wind": 0, "temperature": 285, "cloud-cover": 4},
  '10:00' : {"wind": 0, "temperature": 273, "cloud-cover": 74},
  '11:00' : {"wind": 8, "temperature": 300, "cloud-cover": 14},
  '12:00' : {"wind": 7, "temperature": 294, "cloud-cover": 26},
  '13:00' : {"wind": 6, "temperature": 299, "cloud-cover": 53},
  '14:00' : {"wind": 4, "temperature": 284, "cloud-cover": 42},
  '15:00' : {"wind": 3, "temperature": 284, "cloud-cover": 12},
  '16:00' : {"wind": 2, "temperature": 293, "cloud-cover": 1},
  '17:00' : {"wind": 1, "temperature": 300, "cloud-cover": 9},
  '18:00' : {"wind": 1, "temperature": 302, "cloud-cover": 26},
  '19:00' : {"wind": 1, "temperature": 295, "cloud-cover": 85},
  '20:00' : {"wind": 0, "temperature": 279, "cloud-cover": 42},
  '21:00' : {"wind": 8, "temperature": 288, "cloud-cover": 35},
  '22:00' : {"wind": 3, "temperature": 286, "cloud-cover": 24},
  '23:00' : {"wind": 5, "temperature": 294, "cloud-cover": 1},
}