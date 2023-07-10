import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train1=x_train
x_test1=x_test
x_train = x_train.reshape((-1, 28 * 28)).astype("float32") / 255.0-0.5
x_test = x_test.reshape((-1, 28 * 28)).astype("float32") / 255.0-0.5
y_train = np.eye(10)[y_train.reshape(-1)]



def relu_derivative(x):
    return np.floor(((np.sign(x) + 1) / 2.0))


def relu(x):
    return relu_derivative(x) * x


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


def softmax(x, y):
    maxn = np.max(x, axis=1)

    for i in range(x.shape[0]):
        x[i] -= maxn[i]

    x = np.exp(x)
    total = np.sum(x, axis=1)
    for i in range(x.shape[0]):
        x[i] /= total[i]
    return x


def softmax_derivative(x, y):
    return x - y


def lms(x, y):
    return (x - y) * (x - y) / 2.0


def lms_derivative(x, y):
    return x - y


ACTIVATION = {"relu": relu, "sigmoid": sigmoid}
DERIVATIVE = {"relu": relu_derivative, "sigmoid": sigmoid_derivative}
LOSS_FUNCTION = {"softmax": softmax, "LMS": lms}
LOSS_DERIVATIVE = {"softmax": softmax_derivative, "LMS": lms_derivative}




class Dense:
    def __init__(self, output_size, activation,lr):
        self.size = output_size
        self.activation = ACTIVATION[activation]
        self.derivative = DERIVATIVE[activation]
        self.weight = None

        self.data = None
        self.lr=lr

    def set_weight(self, input_size):
        self.weight = np.random.normal(size=(input_size, self.size),scale=np.sqrt(2 / (input_size * self.size ** 2)))

    def forward(self, input):
        self.data = self.activation(np.dot(input, self.weight))

    def backward(self,prev_record, error):
        tmp=self.weight
        grad=np.dot(prev_record.T, self.derivative(self.data)*error)
        current_grad = self.lr * grad
        self.weight -= current_grad
        return np.dot(tmp, error.T).T


    
    
class Dropout:
    def __init__(self, dropout_rate):
        self.rate=dropout_rate
        self.size=0
        self.arr=None
        self.data=None
        self.count=0
    def set_weight(self,input_size):
        self.size=input_size
    
    def forward(self,input):

        if self.count%100==0:
            self.arr=np.random.binomial(1, 1-self.rate, self.size)
        self.count+=1
        self.data=(input*self.arr)
    def backward(self,prev_record,error):
        return (error*self.arr)




class Input:
    ''' input_size: must be 1 dimension do not have weight '''

    def __init__(self, input_size):
        self.size = input_size
        self.data = None

    def set_data(self, sample):
        self.data = sample

        
class Adam:
    def __init__(self,lr=0.001):
        self.lr=lr
        self.beta1=0.9
        self.beta2=0.999
        self.eps=1e-7
        self.m=list()
        self.v=list()
        self.step=0
    def initialization(a):
        self.m.append(np.zeros(a.shape))
        self.v.append(np.zeros(a.shape))
    def update(self,params,grads):
        self.m
            
        

class ANN:
    def __init__(self, sample_size,epochs, optimizer=None, loss="LMS"):
        if loss == "LMS":
            self.loss_function = LOSS_FUNCTION["LMS"]
            self.loss_derivative = LOSS_DERIVATIVE["LMS"]
        if loss=="softmax":
            self.loss_function = LOSS_FUNCTION["softmax"]
            self.loss_derivative = LOSS_DERIVATIVE["softmax"]
        self.sample_size = sample_size
        self.sequence = list()
        self.loss = list()
        self.epochs=epochs
        
            

    def add(self, other):

        if isinstance(other, Input):
            self.sequence.append(other)
            return
        if isinstance(other, Dense):
            other.set_weight(self.sequence[-1].size)
            self.sequence.append(other)
        if isinstance(other,Dropout):
            other.set_weight(self.sequence[-1].size)
            self.sequence.append(other)

    def train(self, data, labels):
        length = len(self.sequence)
        print(self.epochs)
        
        for j in range(self.epochs):
            if j%100==0:
                begin_sampling = np.random.randint(0, data.shape[0] - self.sample_size)
                data_input = data[begin_sampling:begin_sampling + self.sample_size]
                labels_input=labels[begin_sampling:begin_sampling + self.sample_size]
            

            self.sequence[0].set_data(data_input)

            for i in range(1, length):

                self.sequence[i].forward(self.sequence[i - 1].data)
            
            
            loss = np.sum(self.loss_function(self.sequence[-1].data, labels_input))

            self.loss.append(loss)

            error=self.loss_derivative(self.sequence[-1].data, labels_input)

            for i in range(length-1, 0, -1):
                error = self.sequence[i].backward(self.sequence[i-1].data, error)
            if j%1000==0:
                print("---------epoch:",j," -------------")
            
            
    def predict(self,data_input):
        length = len(self.sequence)
        self.sequence[0].set_data(data_input)

        for i in range(1, length):
            self.sequence[i].forward(self.sequence[i - 1].data)
        return self.sequence[-1].data
        
sample_size=20
Neural = ANN(sample_size,epochs=7000)
Neural.add(Input(28 * 28))
Neural.add(Dropout(0.5))
Neural.add(Dense(128, "relu",0.0013))
Neural.add(Dense(64, "relu",0.001))
Neural.add(Dropout(0.2))
Neural.add(Dense(32, "relu",0.001))
Neural.add(Dense(10, "relu",0.0008))

print(Neural.train(x_train,y_train))
# print(Neural.loss)
# print(Neural.sequence[-1].weight)
plt.plot(Neural.loss)
# print(Neural.sequence[-1].weight)
print("final loss:",Neural.loss[-1])
plt.show()


c=0
tmp=0

for b in range(10000):
    a=Neural.predict(x_train[b:b+1])
    maxn=0
    for i in range(len(a[0])):
        if a[0][maxn]<a[0][i]:
            maxn=i
#     print(a,y_test[b])
#     print(y_train.shape)
    for j in range(len(y_train[b])):
        if y_train[b][j]==1:
            tmp=j
            break
    if maxn==tmp:
        c+=1

print(c/10000)