import time
import functools
import statistics


class Timer:
    def __init__(self,
                 runs=10,
                 print_report=True,
                 round_floats=-1,
                 stats=["mean", "median", "max", "min", "stdev", "total"]):
        str_to_function = {
            "mean": statistics.mean,
            "median": statistics.median,
            "stdev": statistics.stdev,
            "total": sum,
            "min": min,
            "max": max,
        }
        self.func_name = ""
        self.time_series = []
        self.runs = runs
        self.__print_report = print_report
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
            else:
                raise Exception(
                    f"Not sure what to do with {s}, it must be a callable or string"
                )
        self.metrics = metrics

    def print_report(self):
        print(f"Report for: {self.func_name}")
        for metric, value in self.report.items():
            if self.round_floats == -1: print(f"{metric.title()}\t:  {value}")
            else:
                print(f"{metric.title()}\t:  {round(value,self.round_floats)}")
        if "mean" in self.report and "stdev" in self.report:
            mean, stdev = self.report["mean"], self.report["stdev"]
            print(f"\u03bc \u00b1 \u03c3 : {mean:.2f} \u00b1 {stdev:.2f}")

    def __call__(self, input_func, *args, **kwargs):
        self.func_name = input_func.__name__

        def wrapper(*args, **kwargs):
            for _ in range(self.runs):
                start = time.perf_counter()
                rvalue = input_func(*args, **kwargs)
                end = time.perf_counter()
                self.time_series.append(end - start)
            self.report = {
                name: func(self.time_series)
                for name, func in self.metrics.items()
            }
            if self.__print_report:
                self.print_report()
            return rvalue, self.report

        return wrapper


@Timer(runs=3)
def fib(n):
    time.sleep(1)
    f, s = 0, 1
    for _ in range(n):
        f, s = s, f + s
    return f


if __name__ == "__main__":
    result, report = fib(100)
    print(result)
