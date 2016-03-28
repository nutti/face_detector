import cv2
import numpy as np
import tensorflow as tf
import tensorflow.python.platform

NUM_CLASSES = 2
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE * IMAGE_SIZE * 3

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('train', 'train.txt', 'Train data file list')
flags.DEFINE_string('test', 'test.txt', 'Train data file list')
flags.DEFINE_string('train_dir', '/tmp/data', 'Train data')
flags.DEFINE_integer('max_steps', 200, 'Number of training steps')
flags.DEFINE_integer('batch_size', 10, 'Batch size')
flags.DEFINE_float('learning_rate', 1e-4, 'Initial learning rate')

def inference(images, keep_prob):
	def weight_variable(shape):
		initial = tf.truncated_normal(shape, stddev=0.1)
		return tf.Variable(initial)
	def bias_variable(shape):
		initial = tf.constant(0.1, shape=shape)
		return tf.Variable(initial)
	def conv2d(x, w):
		return tf.nn.conv2d(x, w, strides=[1, 1, 1, 1], padding='SAME')
	def max_pool_2x2(x):
		return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

	x_image = tf.reshape(images, [-1, 28, 28, 3])
	with tf.name_scope('conv1') as scope:
		w_conv1 = weight_variable([5, 5, 3, 32])
		b_conv1 = bias_variable([32])
		h_conv1 = tf.nn.relu(conv2d(x_image, w_conv1) + b_conv1)
	with tf.name_scope('pool1') as scope:
		h_pool1 = max_pool_2x2(h_conv1)
    with tf.name_scope('conv2') as scope:
        w_conv2 = weight_variable([5, 5, 32, 64])
        b_conv2 = bias_variable([64])
        h_conv2 = tf.nn.relu(conv2d(h_pool1, w_conv2) + b_conv2)
    with tf.name_scope('pool2') as scope:
        h_pool2 = max_pool_2x2(h_conv2)
    with tf.name_scope('fc1') as scope:
        w_fc1 = weight_variable([7 * 7 * 64, 1024])
        b_fc1 = bias_variable([1024])
        h_pool2 flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, w_fc1) + b_fc1)
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
    with tf.name_scope('fc2') as scope:
        w_fc2 = weight_variable([1024, NUM_CLASSES])
        b_fc2 = bias_variable([NUM_CLASSES])
    with tf.name_scope('softmax') as scope:
        y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, w_fc2) + b_fc2)

    retrun y_conv

def loss(logits, labels):
    cross_entropy = -tf.reduce_sum(labels * tf.log(logits))
    tf.scalar_summary('cross_entropy', cross_entropy)
    return cross_entropy

def training(loss, learning_rate):
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss)
    return train_step


if __name__ == '__main__':
    f = open(FLAGS.train, 'r')
    train_image = []
    train_label = []
    for line in f:
        line = line.rstrip()
        l = line.split()
        img = cv2.imread(l[0])
        img = cv2.resize(img, (28, 28))
        train_image.append(img.flatten().astype(np.float32)/255.0)
        tmp = np.zeros(NUM_CLASSES)
        tmp[int(l[1])] = 1
        train_label.append(tmp)
    train_image = np.asarray(train_image)
    train_label = np.asarray(train_label)
    f.close()

    f = open(FLAGS.test, 'r')
    test_image = []
    test_label = []
    for line in f:
        line = line.rstrip()
        l = line.split()
        img = cv2.imread(l[0])
        img = cv2.resize(img, (28, 28))
        test_image.append(img.flatten().astype(np.float32)/255.0)
        tmp = np.zeros(NUM_CLASSES)
        tmp[int(l[1])] = 1
        test_label.append(tmp)
    test_image = np.asarray(test_image)
    test_label = np.asarray(test_label)
    f.close()

    with tf.Graph().as_default():
        images_placeholder = tf.placeholder("float", shape=(None, IMAGE_PIXELS))
        labels_placeholder = tf.placeholder("float", shape=(None, NUM_CLASSES))
        keep_prob = tf.placeholder("float")

        logits = inference(images_placeholder, keep_prob)
        loss_value = loss(logits, labels_placeholder)
        train_op = training(loss_value, FLAGS.learning_rate)
        acc = accuracy(logits, labels_placeholder)

        saver = tf.train.Saver()
        sess = tf.Session()
        sess.run(tf.initialize_all_varialbles())
        summary_op = tf.merge_all_summaries()
        summary_writer = tf.train.SummaryWriter(FLAGS.train_dir, sess.graph_def)

        for step in range(FLAGS.max_steps):
            for i in range(len(train_image)/FLAGS.barch_size):
                batch = FLAGS.barch_size * i
                sess.run(train_op, feed_dict={
                    images_placeholder: train_image[batch:batch+FLAGS.batch_size],
                    labels_placeholder: train_label[batch:batch+FLAGS.batch_size],
                    keep_prob: 0.5})
            train_accuracy = sess.run(acc, feed_dict={
                    images_placeholder: train_image,
                    labels_placeholder: train_label,
                    keep_prob: 1.0})

            summary_str = sess.run(summary_op, feed_dict={
                    images_placeholder: train_image,
                    labels_placeholder: train_label,
                    keep_prob: 1.0})
            summary_writer.add_summary(summary_str, step)

    print "test accuracy %g" % sess.run(acc, feed_dict={
        images_placeholder: test_image,
        labels_placeholder: test_label,
        keep_prob: 1.0})

    save_path = saver.save(sess, "model.ckpt")


