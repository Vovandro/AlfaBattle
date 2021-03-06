# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13iAJCl2uCHgb05DOUL0d4LFzMa7HB0iT
"""
import sys

import pandas as pd
import numpy as np

from tensorflow import keras
from tensorflow.keras import layers

data = pd.read_csv('../merged_data.csv')

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold

features = [x for x in data.columns if x not in ['app_id', 'flag']]
targets = data.flag.values

oof = np.zeros(len(data))
train_preds = np.zeros(len(data))
models = []

cv = KFold(n_splits=5, random_state=6, shuffle=True)

for fold_, (train_idx, val_idx) in enumerate(cv.split(data, targets), 1):
    print(f'Training with fold {fold_} started.')
    input_layer = layers.Input(len(features))
    layer_0 = layers.Dense(1000)(input_layer)
    layer_1 = layers.Dense(1000, activation='sigmoid')(layer_0)
    layer_2 = layers.Dense(1000, activation='relu')(layer_0)
    layer_3 = layers.Dense(500, activation='sigmoid')(layer_1)
    layer_4 = layers.Dense(500, activation='relu')(layer_2)
    layer_5 = layers.Add()([layer_3, layer_4])
    layer_6 = layers.Dense(300, activation='relu')(layer_5)
    out_layer = layers.Dense(2, activation='softmax')(layer_6)
    model = keras.Model(inputs=input_layer, outputs=out_layer)

    model.compile(optimizer=keras.optimizers.Adam(0.0001), loss=keras.losses.categorical_crossentropy, metrics=[keras.metrics.AUC(name='auc'), 'acc'])

    model.summary()

    checkpoint = keras.callbacks.ModelCheckpoint(f"{fold_}model.hdf5", monitor='val_auc', verbose=0
                                                 , save_best_only=True, mode='max')

    train, val = data.iloc[train_idx], data.iloc[val_idx]

    model.fit(train[features], keras.utils.to_categorical(train.flag, 2), epochs=30, verbose=1,
              validation_data=(val[features], keras.utils.to_categorical(val.flag, 2)), callbacks=[checkpoint])

    #oof[val_idx] = model.predict_proba(val[features])[:, 1]

    #train_preds[train_idx] += model.predict_proba(train[features])[:, 1] / (cv.n_splits-1)
    models.append(model)
    print(f'Training with fold {fold_} completed.')


#metrics = roc_auc_score(y_test, train_preds)
#print(metrics)

del data

test_data = pd.read_csv('../merged_test_data.csv')

features = [x for x in test_data.columns if x not in ['app_id', 'flag']]
score = np.zeros(len(test_data))

for m in models:
    score += np.argmax(m.predict(test_data[features]), axis=1) / len(models)
    
submission = pd.DataFrame({
    'app_id' : test_data.app_id.values,
    'flag': score
}) # ~ 0.732 на public test

submission.to_csv('keras_first.csv', index=None)
