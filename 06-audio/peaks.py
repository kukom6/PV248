import wave
import numpy
import sys
import struct


def main():
    if len(sys.argv) != 2:
        print("Numbers of parameter are wrong")
    else:
        file = wave.open(sys.argv[1], 'r')
        number_of_channel = file.getnchannels()
        number_of_frames = file.getnframes()
        framerate = file.getframerate()
        # https://stackoverflow.com/questions/2226853/interpreting-wav-data
        total_samples = number_of_frames * number_of_channel
        fmt = "{}h".format(total_samples)

        all_data = struct.unpack(fmt, file.readframes(file.getnframes()))
        if number_of_channel is 2:
            all_data = convert_to_mono(all_data)  # shrink to mono
        windows = cut_into_windows(all_data, framerate, number_of_frames)

        min_value = None
        max_value = None

        for window in windows:
            numpy_array = numpy.array(window)
            results = numpy.abs(numpy.fft.rfft(numpy_array))
            average = numpy.average(results)
            peak_threshold = average*20

            for index, result in enumerate(results):
                if result >= peak_threshold:
                    if min_value is None or index < min_value:
                        min_value = index
                    if max_value is None or index > max_value:
                        max_value = index
        if max_value is None and min_value is None:
            print('no peaks')
        elif max_value is not None and min_value is not None:
            print('low = {}, high = {}'.format(min_value, max_value))
        else: # just for sure
            sys.stderr.write("ERROR: Only LOW or HIGH was set. LOW = {}, HIGT = {}".format(min_value, max_value))


# Cut all data from wav to the array of arrays (windows) according to size of window.
def cut_into_windows(data, framerate, number_of_frames):
    result=[]
    number_of_windows = int(number_of_frames // framerate)  # size of window
    counter = 0 # counter
    for _ in range(0, number_of_windows):
        window = []
        for __ in range(0,framerate):
            window.append(data[counter])
            counter += 1
        result.append(window)
    return result


# function convert array to array where average from two item from input array are added to output array
# e.g. [1, 3, 5, 8] -> [2, 6.5]
# for odd number [1, 3, 5] -> [2, 5]
def convert_to_mono(array):
    result_array = []
    iterator = iter(array)
    for item in iterator:
        next_item = next(iterator, None)
        if next_item is None:
            result_array.append(item)
        else:
            result_array.append((item+next_item)/2)
    return result_array


main()