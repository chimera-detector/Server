# usr/bin/python27


# Import relevant packages and modules
from utils import *
import random
import tensorflow as tf
import sys, os


# Set file names
file_train_instances = "stance/train_stances.csv"
file_train_bodies = "stance/train_bodies.csv"
file_test_instances = "stance/test_stances_unlabeled.csv"
file_test_bodies = "stance/test_bodies.csv"
file_predictions = 'stance/predictions_oneline.csv'

class Detector ():
    def __init__(self):
        return None

    def detect(self, headline, content):

        # Initialise hyperparameters
        r = random.Random()
        lim_unigram = 5000
        target_size = 4
        hidden_size = 100
        train_keep_prob = 0.6
        l2_alpha = 0.00001
        learn_rate = 0.01
        clip_ratio = 5
        batch_size_train = 500
        epochs = 90


        # Load data sets
        raw_train = FNCData(file_train_instances, file_train_bodies)
        raw_test = FNCData(file_test_instances, file_test_bodies)
        n_train = len(raw_train.instances)


        # Process data sets
        train_set, train_stances, bow_vectorizer, tfreq_vectorizer, tfidf_vectorizer = \
            pipeline_train(raw_train, raw_test, lim_unigram=lim_unigram)
        feature_size = len(train_set[0])
        test_set = pipeline_test(raw_test, bow_vectorizer, tfreq_vectorizer, tfidf_vectorizer)


        # Define model

        # Create placeholders
        features_pl = tf.placeholder(tf.float32, [None, feature_size], 'features')
        stances_pl = tf.placeholder(tf.int64, [None], 'stances')
        keep_prob_pl = tf.placeholder(tf.float32)

        # Infer batch size
        batch_size = tf.shape(features_pl)[0]

        # Define multi-layer perceptron
        hidden_layer = tf.nn.dropout(tf.nn.relu(tf.contrib.layers.linear(features_pl, hidden_size)), keep_prob=keep_prob_pl)
        logits_flat = tf.nn.dropout(tf.contrib.layers.linear(hidden_layer, target_size), keep_prob=keep_prob_pl)
        logits = tf.reshape(logits_flat, [batch_size, target_size])

        # Define L2 loss
        tf_vars = tf.trainable_variables()
        l2_loss = tf.add_n([tf.nn.l2_loss(v) for v in tf_vars if 'bias' not in v.name]) * l2_alpha

        # Define overall loss
        loss = tf.reduce_sum(tf.nn.sparse_softmax_cross_entropy_with_logits(logits, stances_pl) + l2_loss)

        # Define prediction
        softmaxed_logits = tf.nn.softmax(logits)
        predict = tf.arg_max(softmaxed_logits, 1)

        with tf.Session() as sess:
            load_model(sess)

            # Predict
            test_feed_dict = {features_pl: test_set, keep_prob_pl: 1.0}
            test_pred = sess.run(predict, feed_dict=test_feed_dict)

        # Save predictions
        save_predictions(test_pred, file_predictions)
        stance = check_predictions(file_predictions)

        return stance

    def save_testData(self, headline, content):
        # TODO: Keep this file has only one line of rows
        with open(file_test_instances, 'w') as csvfile:
            fieldnames = ['Headline', 'Body ID']
            writer = DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({'Headline': headline, 'Body ID': 1})

        with open(file_test_bodies, 'w') as csvfile:
            fieldnames = ['Body ID', 'articleBody']
            writer = DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({'Body ID': 1, 'articleBody': content})

detector = Detector()

if __name__ == "__main__":
    print("stance is: {0}".format(detector.detect(sys.argv[1], sys.argv[2])))
