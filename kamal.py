import argparse
import ast
import csv
import importlib
import os
import sys

from functools import cmp_to_key

import jedi
import pandas as pd


def cmp_None_last(a, b):
    if a is None:
        return +1
    if b is None:
        return -1
    return -1 if a < b else 1


def read_code(top_dir):
    """Read code from each Python file in and below `top_dir`."""
    for root, dirs, files in os.walk(top_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue

            with open(os.path.join(root, fname)) as f:
                print(os.path.join(root, fname))
                yield f.read()


def analyze_code(code, module, debug=False):
    """Collect statistics about usage of module API in a code snippet"""
    ast_ = ast.parse(code)
    s = jedi.Script(code)

    for node in ast.walk(ast_):
        if isinstance(node, ast.Call):
            if debug:
                print(ast.get_source_segment(code, node))
            lineno = node.func.lineno
            # make sure we don't end up on the end of the line
            # Get the source from which node comes, look at the first line's length
            # and use the smaller of end_col_offset or line length
            column = (
                min(
                    len(ast.get_source_segment(code, node).split("\n")[0]),
                    node.func.end_col_offset,
                )
                - 1
            )
            inferred = s.goto(line=lineno, column=column)
            if inferred:
                inferred = inferred[0]
            else:
                continue

            func_name = inferred.full_name
            if func_name is None:
                inferred_ = s.infer(line=lineno, column=column)
                if inferred_:
                    func_name = s.infer(line=lineno, column=column)[0].full_name
                else:
                    # too weird, we skip this
                    continue

            # "Infer" one more level up if the thing we found is defined in the main script
            if func_name.startswith("__main__"):
                next_inferred = inferred.infer()
                if next_inferred:
                    next_func_name = next_inferred[0].full_name
                    # Only overwrite func_name if the next name is actually useful
                    if next_func_name is not None:
                        func_name = next_func_name

            args = []
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    value = arg.id
                elif isinstance(arg, ast.Constant):
                    value = str(arg.value)
                # Placeholder for values we don't recognise, e.g. expressions
                else:
                    value = "**"

                args.append(value)

            kwargs = {}
            for kwarg in node.keywords:
                name = kwarg.arg
                if isinstance(kwarg.value, ast.Name):
                    value = kwarg.value.id
                elif isinstance(kwarg.value, ast.Constant):
                    value = kwarg.value.value
                # Placeholder for values we don't recognise, e.g. expressions
                else:
                    value = "**"

                kwargs[name] = value

            args_ = ", ".join(v for v in args)
            # Handle the case of **kwargs a la: foo(arg=1, **kwargs) which is
            # represented as a keyword node but without a name
            kwargs_ = ", ".join(
                [
                    f"{k}={kwargs[k]}"
                    for k in sorted(kwargs, key=cmp_to_key(cmp_None_last))
                    if k is not None
                ]
            )
            if None in kwargs:
                if kwargs_:
                    kwargs_ += ", "
                kwargs_ += f"**{kwargs[None]}"

            if debug:
                print(f'L{node.lineno} "{func_name}" "{args_}" "{kwargs_}"')

            if func_name.startswith(module):
                # yield {"func": func_name, "args": args, "kwargs": kwargs}
                # yield f"{func_name}({args_}, {kwargs_})"
                yield {"function": func_name, "args": args_, "kwargs": kwargs_}


def generate_(codes, module):
    for code in codes:
        for inst in analyze_code(code, module=module):
            yield inst


def get_argparser():
    parser = argparse.ArgumentParser(description="kamal - A simple API usage analyser")
    parser.add_argument(
        "--module",
        help="Module name to collect usage statistics about",
        default="sklearn",
    )
    parser.add_argument(
        "--output", help="File to store output CSV in", default="statistics.csv"
    )
    parser.add_argument(
        "source_directory", help="Directory containing source code to analyze"
    )

    return parser


def main():
    parser = get_argparser()
    args = parser.parse_args()

    if importlib.util.find_spec("sklearn") is None:
        sys.exit(f"Install the '{args.module}' module to collect statistics about its usage.")

    with open(args.output, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["function", "args", "kwargs"])
        writer.writeheader()

        for code in read_code(args.source_directory):
            for inst in analyze_code(code, module=args.module):
                writer.writerow(inst)

    # df = pd.DataFrame.from_records(
    #     generate_(read_code(args.source_directory), module=args.module),
    #     columns=("function", "args", "kwargs"),
    # )


if __name__ == "__main__":
    main()
