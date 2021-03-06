
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix
import pandas as pd

#Gerando novas imagens a partir do dataset

train_datagen = ImageDataGenerator(preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
                                   rotation_range=50, width_shift_range=0.2,
                                   height_shift_range=0.2, zoom_range=0.1,
                                   horizontal_flip=True, vertical_flip=True)

train_generator = train_datagen.flow_from_directory('/content/dataset_cats_and_dogs/training_set',
                                               target_size=(224, 224),
                                               batch_size=16,
                                               class_mode='categorical',
                                               shuffle=True)

step_size_train = train_generator.n // train_generator.batch_size

test_datagen = ImageDataGenerator(preprocessing_function=tf.keras.applications.resnet50.preprocess_input)

test_generator = test_datagen.flow_from_directory('/content/dataset_cats_and_dogs/test_set',
                                                  target_size=(224, 224),
                                                  batch_size=16,
                                                  class_mode='categorical',
                                                  shuffle=False)

step_size_test = test_generator.n // test_generator.batch_size

#Carregando modelo imagenet

base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)
print(base_model.summary())

#Rede Neural

x = base_model.output
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dense(1024, activation='relu')(x)
x = tf.keras.layers.Dense(1024, activation='relu')(x)
x = tf.keras.layers.Dense(512, activation='relu')(x)
preds = tf.keras.layers.Dense(2, activation='softmax')(x)

model = tf.keras.Model(inputs = base_model.input, outputs = preds)

print(model.summary())

for i, layer in enumerate(model.layers):
    print(i, layer.name)
    
for layer in model.layers[:175]:
    layer.trainable = False
for layer in model.layers[175:]:
    layer.trainable = True

#Treinamento

model.compile(optimizer = 'Adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
history = model.fit_generator(generator = train_generator,
                              epochs = 30,
                              steps_per_epoch = step_size_train,
                              validation_data = test_generator,
                              validation_steps = step_size_test)

print(np.mean(history.history['val_accuracy']))
print(np.std(history.history['val_accuracy']))

model.save('model.h5', save_format='h5')

#Gráficos

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.show()


plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.show()


#Matriz de confusão

filenames = test_generator.filenames
print(filenames)
print(len(filenames))

predictions = model.predict_generator(test_generator, steps=len(filenames))
print(predictions)
print(len(predictions))

predictions2 = []
for i in range(len(predictions)):
    predictions2.append(np.argmax(predictions[i]))

print(predictions2)
print(test_generator.classes)
print(test_generator.class_indices)

accuracy_score(predictions2, test_generator.classes)
cm = confusion_matrix(predictions2, test_generator.classes)

index = ['cats', 'dogs']
columns = ['cats', 'dogs']
cm_df = pd.DataFrame(cm, columns, index)
plt.figure(figsize=(10,6))
plt.title('Confusion Matrix')
sns.heatmap(cm_df, annot=True)
