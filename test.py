tradesData = {}


def test_function():
    dataToWrite = {
        'response': 0,
        'orderPlacementStatus': 1,
        'strikes': [],
        'strikesLTPEntry': [],
        'spotLTPEntry': 43000,
        'orderData': [],
        'orderEntryResponse': []
    }
    tradesData = dataToWrite
    print(tradesData)

    dataToWrite = {
        'strikesLTPExit': [],
        'spotLTPExit': 50000,
        'pnl': 0,
        'orderExitResponse': []
    }

    combinedDataToWrite = dict(list(tradesData.items()) + list(dataToWrite.items()))
    tradesData = combinedDataToWrite
    print(tradesData)

test_function()