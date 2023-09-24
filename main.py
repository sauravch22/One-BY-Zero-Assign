from flask import Flask, request, jsonify
import statistics
app = Flask(__name__)
list_Samples = []
Intervals = []


def readintervals():
    with open("input.txt", "r") as file:
        for line in file:
            content = line.split(",")
            Intervals.append([float(content[0]), float(content[1])])


@app.route('/api/v1/insertSamples', methods=['POST'])
def insertSamples():
    samples = request.get_json()
    for number in samples['Samples']:
        list_Samples.append(number)
    return "Samples Entered Successfully"


@app.route('/api/v1/metrics', methods=['GET'])
def metrics():
    Intervals.sort()
    non_overlap_Interval = []
    non_outliers = []
    outliers = []
    end = Intervals[0][1]
    non_overlap_Interval.append([Intervals[0][0], Intervals[0][1]])
    for i in range(1, len(Intervals), 1):
        if Intervals[i][0] >= end:
            non_overlap_Interval.append([Intervals[i][0], Intervals[i][1]])
            end = Intervals[i][1]

    frequency = [0] * len(non_overlap_Interval)
    mean = 0
    count = 0
    for samples in list_Samples:
        flag = True
        for i in range(0, len(non_overlap_Interval), 1):
            if non_overlap_Interval[i][0] <= samples < non_overlap_Interval[i][1]:
                non_outliers.append(samples)
                frequency[i] = frequency[i] + 1
                flag = False
                break
        if flag:
            outliers.append(samples)

    result = []
    for i in range(0,len(non_overlap_Interval),1):
        result.append(["[",non_overlap_Interval[i][0],non_overlap_Interval[i][1],")",frequency[i]])

    return_json = {
        "Frequency" : result,
        "sample mean: ": statistics.mean(non_outliers),
        "sample variance: ": statistics.variance(non_outliers),
        "outliers :": outliers
    }
    return jsonify(return_json)


if __name__ == '__main__':
    readintervals()
    app.run(debug=True)
