# Description: Standard date, time units used in pandas and numpy.
# Author: Jaswant Sai Panchumarti

DATE = ['Y', 'M', 'W', 'D']
TIME = ['h', 'm', 's']
PRECISE_TIME = ['ms', 'us', 'ns']
DATE_TIME = [*DATE, *TIME]
DATE_TIME_PRECISE = [*DATE_TIME, *PRECISE_TIME]