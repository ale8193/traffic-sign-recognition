import logging
from time import gmtime, strftime

from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, MaxPool2D, Dropout
from keras.optimizers import SGD
from keras.models import model_from_json
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard, CSVLogger, LearningRateScheduler

from src.models.callbacks.LogCallback import LogCallback

callback_table = {
    'LogCallback': {
        'class': LogCallback,
        'args': {
            'log_file': 'log/model.log',
            'level': logging.INFO,
            'format': '%(levelname)s: %(asctime)s: %(message)s'
        }
    },
    'CSVLogger': {
        'class': CSVLogger,
        'args': {
            'filename': 'log/last_history.csv',
            'separator': ',',
            'append': False
        }
    },
    'ModelCheckpoint': {
        'class': ModelCheckpoint,
        'args': {
            'filepath': 'model/checkpoints/weights-{epoch:02d}-{val_loss:.2f}.hdf5',
            'monitor': 'val_loss',
            'verbose': 0,
            'save_best_only': True,
            'save_weights_only': True,
            'mode': 'auto',
            'period': 1
        }
    },
    'EarlyStopping': {
        'class': EarlyStopping,
        'args': {
            'monitor': 'val_loss',
            'min_delta': 0,
            'patience': 2,
            'verbose': 0,
            'mode': 'auto',
            'baseline': None,
            'restore_best_weights': True
        }
    },
    # TensorBoard will be added at every fit execution to allow to change the name of log_dir based on the time stamp
    # 'TensorBoard': {
    #     'class': TensorBoard,
    #     'args': {
    #         'log_dir': 'log/tensorboard-logs'
    #     }
    # }
}


class Model:

    def __init__(self, name='Simple Model', auto_save=True, layer_activation='relu', num_output=43,
                 output_activation='softmax', kernel_size=3, input_shape=(46, 46), lr=0.01):
        self.model = None
        self.name = name
        self.auto_save = auto_save
        self.layers_activation = layer_activation
        self.num_output = num_output
        self.output_activation = output_activation
        self.kernel_size = kernel_size
        self.input_shape = input_shape
        self.lr = lr
        self.callbacks = list()

    def __str__(self):
        return self.name

    def create_model(self):
        model = Sequential()

        model.add(Conv2D(filters=32, kernel_size=self.kernel_size, activation=self.layers_activation,
                         strides=(1, 1), padding='same', input_shape=self.input_shape))
        model.add(MaxPool2D(pool_size=(2, 2), strides=2))
        model.add(Dropout(0.2))

        model.add(Conv2D(filters=64, kernel_size=self.kernel_size, activation=self.layers_activation, strides=(1, 1),
                         padding='valid'))
        model.add(MaxPool2D(pool_size=(2, 2), strides=2))
        model.add(Dropout(0.2))

        model.add(Conv2D(filters=128, kernel_size=self.kernel_size, activation=self.layers_activation, strides=(1, 1),
                         padding='valid'))
        model.add(MaxPool2D(pool_size=(2, 2), strides=2))
        model.add(Dropout(0.2))

        model.add(Flatten())

        # Add the output layer
        model.add(Dense(self.num_output, activation=self.output_activation))
        self.model = model
        return self.model

    def compile(self, optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'], decay=1e-6, momentum=0.9,
                nesterov=True):
        sgd = SGD(lr=self.lr, decay=decay, momentum=momentum, nesterov=nesterov)
        self.model.compile(loss=loss, optimizer=sgd, metrics=metrics)

    def fit(self, train_data, train_labels, validation_split=0.25, epochs=10, batch_size=100):

        if self.auto_save:
            self.auto_save_model()
        history = self.model.fit(train_data, train_labels, validation_split=validation_split, epochs=epochs,
                                 batch_size=batch_size, callbacks=self.callbacks_pre_fit(int(batch_size)))
        if self.auto_save:
            self.auto_save_weights(epochs)
        return history

    def fit_generator(self, generator, steps_per_epoch=1000, epochs=10, validation_data=None, validation_steps=None,
                      workers=1, use_multiprocessing=False, initial_epoch=0):
        if self.auto_save:
            self.auto_save_model()
        history = self.model.fit_generator(generator, steps_per_epoch=int(steps_per_epoch), epochs=int(epochs),
                                           validation_data=validation_data,
                                           validation_steps=validation_steps,
                                           callbacks=self.callbacks_pre_fit(int(steps_per_epoch)),
                                           workers=workers,
                                           use_multiprocessing=use_multiprocessing,
                                           initial_epoch=initial_epoch)
        if self.auto_save:
            self.auto_save_weights(epochs)
        return history

    def evaluate(self, test_data, test_labels, batch_size=None, verbose=1):
        return self.model.evaluate(test_data, test_labels, batch_size=batch_size, verbose=verbose)

    def evaluate_generator(self, generator, steps=1000, workers=1, verbose=1):
        return self.model.evaluate_generator(generator, steps=steps, workers=workers, use_multiprocessing=False,
                                             verbose=verbose)

    def predict(self, data, batch_size=None, verbose=1, steps=None):
        return self.model.predict(data, batch_size=batch_size, verbose=verbose, steps=steps)

    def predict_generator(self, generator, steps=None, callbacks=None, max_queue_size=10, workers=1,
                          use_multiprocessing=False, verbose=0):
        return self.model.predict_generator(generator, steps, callbacks, max_queue_size, workers, use_multiprocessing,
                                            verbose)

    def auto_save_model(self):
        path = 'model/' + self.model_name_mode_now_to_string(True) + '.json'
        print('Saving model to: ' + path)
        self.save_model(path)

    def auto_save_weights(self, epochs):
        path = 'model/weights/' + self.model_name_mode_now_to_string() + '.h5'
        print('Saving weights to: ' + path)
        self.save_weights(path)

    def save_model(self, out_path):
        json_model = self.model.to_json()
        with open(out_path, 'w') as outfile:
            outfile.write(json_model)

    def save_weights(self, out_path):
        self.model.save_weights(out_path)

    def load_model(self, file):
        try:
            json_file = open(file, 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            self.model = model_from_json(loaded_model_json)
        except FileNotFoundError:
            print(file + ' not found')

    def load_weights(self, file):
        try:
            self.model.load_weights(file)
        except FileNotFoundError:
            print(file + ' not found')

    def init_callbacks(self, callbacks_names=tuple(
        ('LogCallback', 'CSVLogger', 'ModelCheckpoint', 'TensorBoard')),  # Removed EarlyStopping
                       callbacks=None):
        if callbacks_names is None and callbacks is not None:
            self.callbacks = callbacks
        else:
            for type in callbacks_names:
                try:
                    callback = callback_table[type]['class']
                except KeyError:
                    callback = None
                if callback is not None:
                    self.callbacks.append(callback(**callback_table[type]['args']))

    def callbacks_pre_fit(self, steps_per_epoch):
        if len(self.callbacks) == 0:
            callbacks = None
        else:
            lr = self.lr

            def lr_schedule(epoch):
                return lr * (0.1 ** int(epoch / 10))

            callbacks = self.callbacks
            callbacks.append(TensorBoard(log_dir=self.get_tensorboard_name(), write_grads=True,
                                         batch_size=steps_per_epoch, write_images=True))

            callbacks.append(
                CSVLogger(filename='log/history_' + self.model_name_mode_now_to_string() + '.csv', separator=',',
                          append=False))

            callbacks.append(LearningRateScheduler(lr_schedule))

        return callbacks

    def name_to_file(self):
        return self.name.replace(' ', '_').lower()

    def model_name_mode_now_to_string(self, short=False):
        if short:
            now = ''
        else:
            now = strftime("%d-%m-%Y_%H-%M", gmtime())
        try:
            if self.input_shape[2] == 3:
                color = 'rgb'
            else:
                color = 'grayscale'
        except IndexError:
            color = 'grayscale'
        return self.name_to_file() + '-' + color + '-' + str(now)

    def get_tensorboard_name(self):
        return 'log/tensorboard-' + self.model_name_mode_now_to_string()


def get_value_if_list_or_int(value, index):
    if type(value) is list:
        return value[index]
    else:
        return value
