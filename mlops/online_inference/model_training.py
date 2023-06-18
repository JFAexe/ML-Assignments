import pickle

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from src.constants import MODEL_PATH

FILE_PATH = 'data/TelcoCustomerChurn.csv'

PARAMS = {
    'N_ESTIMATORS': 100,
    'MAX_FEATURES': 0.25,
    'MAX_SAMPLES': 0.15,
    'TEST_SIZE': 0.25,
    'RANDOM_STATE': 42
}

MODEL_TYPE = RandomForestClassifier(
    n_estimators=PARAMS['N_ESTIMATORS'],
    max_features=PARAMS['MAX_FEATURES'],
    max_samples=PARAMS['MAX_SAMPLES'],
    random_state=PARAMS['RANDOM_STATE']
)

NUMERIC_COLS = [
    'tenure',
    'monthly_charges',
    'total_charges'
]

ONEHOT_COLS = [
    'internet_service',
    'payment_method',
    'contract',
    'multiple_lines',
    'online_security',
    'online_backup',
    'device_protection',
    'tech_support',
    'streaming_tv',
    'streaming_movies'
]

ORDINAL_COLS = [
    'gender',
    'senior_citizen',
    'partner',
    'dependents',
    'phone_service',
    'paperless_billing',
]

TARGET_COL = 'churn'

preprocessor = ColumnTransformer([
    ('scaler', StandardScaler(), NUMERIC_COLS),
    ('onehot', OneHotEncoder(), ONEHOT_COLS),
    ('ordinal', OrdinalEncoder(), ORDINAL_COLS),
])

df = pd.read_csv(FILE_PATH)

X = df.drop(columns=TARGET_COL)
y = df[TARGET_COL]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    random_state=PARAMS['RANDOM_STATE'],
    test_size=PARAMS['TEST_SIZE'],
    shuffle=True,
    stratify=y
)

model = Pipeline([
    ('preprocessor', preprocessor),
    ('model', MODEL_TYPE)
])

model.fit(X_train, y_train)

pred = model.predict(X_test)

print('model params', PARAMS)
print('accuracy_score', accuracy_score(y_test, pred))

with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)
