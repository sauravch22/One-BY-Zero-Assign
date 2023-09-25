from flask import Flask, request, jsonify
import statistics
import threading
import sys

app = Flask(__name__)
list_Samples = []
Intervals = []
non_outliers = []
outliers = []
lock = threading.Lock()


def readintervals(path):
    with open(path, "r") as file:
        for line in file:
            content = line.split(",")
            Intervals.append([float(content[0]), float(content[1])])


@app.route('/api/v1/insertSamples', methods=['POST'])
def insertSamples():
    samples = request.get_json()
    for number in samples['Samples']:
        list_Samples.append(number)
    return "Samples Entered Successfully"


def cal_frequency(intervals, frequency, element):
    lock.acquire()
    flag = True
    for i in range(0, len(intervals), 1):
        if intervals[i][0] <= element < intervals[i][1]:
            non_outliers.append(element)
            frequency[i] = frequency[i] + 1
            flag = False
            break

    if flag:
        outliers.append(element)
    lock.release()


@app.route('/api/v1/metrics', methods=['GET'])
def metrics():
    Intervals.sort()
    non_overlap_Interval = []
    threads = []
    outliers.clear()
    end = Intervals[0][1]
    non_overlap_Interval.append([Intervals[0][0], Intervals[0][1]])
    for i in range(1, len(Intervals), 1):
        if Intervals[i][0] >= end:
            non_overlap_Interval.append([Intervals[i][0], Intervals[i][1]])
            end = Intervals[i][1]

    if(len(non_overlap_Interval) < len(Intervals)) :
        print("Some overlapping Intervals present taking the first occuring interval range wise in that case")

    frequency = [0] * len(non_overlap_Interval)
    for samples in list_Samples:
        t = threading.Thread(target=cal_frequency, args=(non_overlap_Interval, frequency, samples,))
        t.start()
        threads.append(t)

    for th in threads:
        th.join()

    result = []
    for i in range(0, len(non_overlap_Interval), 1):
        result.append(["[", non_overlap_Interval[i][0], non_overlap_Interval[i][1], ")", frequency[i]])

    return_json = {
        "Frequency": result,
        "sample mean: ": statistics.mean(non_outliers),
        "sample variance: ": statistics.variance(non_outliers),
        "outliers :": outliers
    }
    return jsonify(return_json)


if __name__ == '__main__':
    path = sys.argv[1]
    readintervals(path)
    app.run(debug=True)
