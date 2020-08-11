import time
import functools
import statistics
from typing import Iterable


class Timer:
    """
    The Timer decorator uses statistical profiling to benchmark running times of a function. 
    The decorated function will return its return value as well as report as dictionary.
    The report dictionary will contain various metrics, which can be customized using stats kwarg

    **Warning**: The decorator is run for every function call. So avoid using recursive functions
    Instead wrap the recursive function with another function to benchmark it.

    Example code-block::

        @Timer(runs=3)
        def func(n):
            time.sleep(1)
            return n
        
        # Run func 3 times and get the mean,max,min,etc of running time in report
        return_value, report = func(42)

    """
    def __init__(self,
                 runs: int,
                 print_report: bool = True,
                 round_floats: int = -1,
                 stats: Iterable = [
                     "mean", "median", "max", "min", "stdev", "total"
                 ]):
        str_to_function = {
            "mean": statistics.mean,
            "median": statistics.median,
            "stdev": statistics.stdev,
            "total": sum,
            "min": min,
            "max": max,
        }
        """
        Keyword arguments:

        :param runs: 
            The number of times to run the function. 
            As running once can return spurious results.
            It is recommended to benchmark against multiple runs

        :param print_report:
            Should the running report be printed to console
            Default: True

        :param round_floats:
            Round floating point numbers to specified precision of decimal places
            If -1, no rounding is performed
            Default: -1

        :param stats:
            The statistics that will be added to report.
            Supported statistics:
                * mean
                * median
                * min
                * max
                * stdev: Standard deviation, not available if runs = 1
                * total: Total of time for all runs

            The parameter also supports custom functions.
            The function will be given total time the function took for each run in a list.
            The function must return a single value that will mapped as key in the report
            
            **Warning**: The key in report will be the function name so avoid lambda

            Default: ["mean", "median", "max", "min", "stdev", "total"]


        :raises KeyError: When stats contains a string containing invalid metric

        """
        self.func_name = ""
        self.runs = runs
        self.print_report = print_report
        self.round_floats = round_floats
        self.report = {}
        metrics = {}
        for s in stats:
            if isinstance(s, str):
                if s in str_to_function:
                    metrics[s] = str_to_function[s]
                else:
                    raise KeyError(
                        f"No such function {s}, available functions: {str_to_function.keys()}"
                    )
            elif callable(s):
                metrics[s.__name__] = s
        if runs == 1 and "stdev" in metrics:
            # Standard deviation cannot be calculated for 1 run
            del metrics["stdev"]
        self.metrics = metrics

    def __print_report(self):
        print(f"Report for: {self.func_name}")
        for metric, value in self.report.items():
            if self.round_floats == -1:
                print(f"{metric.title()}\t:  {value}")
            else:
                print(f"{metric.title()}\t:  {round(value,self.round_floats)}")

        # Pretty print mean and standard deviation
        if all(x in self.report for x in ["stdev", "mean"]):
            mean, stdev = self.report["mean"], self.report["stdev"]
            print(
                f"Approximate running time (\u03bc \u00b1 \u03c3) : {mean:.2f} \u00b1 {stdev:.2f} seconds"
            )

    def __call__(self, input_func, *args, **kwargs):
        # Will be  used by __print_report
        self.func_name = input_func.__name__

        def wrapper(*args, **kwargs):

            # Calculate time elapsed for function and append it to time_series
            time_series = []
            for _ in range(self.runs):
                start = time.perf_counter()
                rvalue = input_func(*args, **kwargs)
                end = time.perf_counter()
                time_series.append(end - start)

            # Run statistical metrics on time_series
            self.report = {
                name: func(time_series)
                for name, func in self.metrics.items()
            }
            if self.print_report:
                self.__print_report()
            return rvalue, self.report

        return wrapper
