__author__ = "James Large"

import keras
import numpy as np

from sktime_dl.deeplearning.base.estimators._classifier import BaseDeepClassifier
from sktime_dl.deeplearning.encoder._base import EncoderNetwork


class EncoderClassifier(BaseDeepClassifier, EncoderNetwork):
    """Encoder

    Adapted from the implementation from Fawaz et. al

    https://github.com/hfawaz/dl-4-tsc/blob/master/classifiers/encoder.py

    Network originally defined in:

    @article{serra2018towards,
       title={Towards a universal neural network encoder for time series},
       author={Serr{\`a}, J and Pascual, S and Karatzoglou, A},
       journal={Artif Intell Res Dev Curr Chall New Trends Appl},
       volume={308},
       pages={120},
       year={2018}
    }
    """

    def __init__(self,
                 nb_epochs=100,
                 batch_size=12,

                 random_seed=0,
                 verbose=False,
                 model_name="encoder",
                 model_save_directory=None):
        super().__init__(
            model_name=model_name, 
            model_save_directory=model_save_directory)
        EncoderNetwork.__init__(self, random_seed=random_seed)
        '''
        :param nb_epochs: int, the number of epochs to train the model
        :param batch_size: int, specifying the length of the 1D convolution window
        :param random_seed: int, seed to any needed random actions
        :param verbose: boolean, whether to output extra information
        :param model_name: string, the name of this model for printing and file writing purposes
        :param model_save_directory: string, if not None; location to save the trained keras model in hdf5 format
        '''

        self.verbose = verbose
        self.is_fitted_ = False

        # calced in fit
        self.input_shape = None
        self.history = None

        # predefined
        self.nb_epochs = nb_epochs
        self.batch_size = batch_size
        self.callbacks = None

    def build_model(self, input_shape, nb_classes, **kwargs):
        """
        Construct a compiled, un-trained, keras model that is ready for training
        ----------
        input_shape : tuple
            The shape of the data fed into the input layer
        nb_classes: int
            The number of classes, which shall become the size of the output layer
        Returns
        -------
        output : a compiled Keras Model
        """
        input_layer, output_layer = self.build_network(input_shape, **kwargs)
        output_layer = keras.layers.Dense(nb_classes, activation='softmax')(output_layer)

        model = keras.models.Model(inputs=input_layer, outputs=output_layer)

        model.compile(loss='categorical_crossentropy', optimizer=keras.optimizers.Adam(0.00001),
                      metrics=['accuracy'])

        self.callbacks = []

        return model

    def fit(self, X, y, input_checks=True, **kwargs):
        """
        Build the classifier on the training set (X, y)
        ----------
        X : array-like or sparse matrix of shape = [n_instances, n_columns]
            The training input samples.  If a Pandas data frame is passed, column 0 is extracted.
        y : array-like, shape = [n_instances]
            The class labels.
        input_checks: boolean
            whether to check the X and y parameters
        Returns
        -------
        self : object
        """
        X = self.check_and_clean_data(X, y, input_checks=input_checks)

        y_onehot = self.convert_y(y)
        self.input_shape = X.shape[1:]

        self.model = self.build_model(self.input_shape, self.nb_classes)

        if self.verbose:
            self.model.summary()

        self.history = self.model.fit(X, y_onehot, batch_size=self.batch_size, epochs=self.nb_epochs,
                                      verbose=self.verbose, callbacks=self.callbacks)

        self.save_trained_model()
        self.is_fitted_ = True

        return self