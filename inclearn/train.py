import random

import numpy as np
import torch

from inclearn import factory, results_utils, utils


def train(args):
    _set_seed(args["seed"])

    factory.set_device(args)

    train_set = factory.get_data(args, train=True)
    test_set = factory.get_data(args, train=False, classes_order=train_set.classes_order)

    train_loader, val_loader = train_set.get_loader(args["validation"])
    test_loader, _ = test_set.get_loader()

    model = factory.get_model(args)

    results = results_utils.get_template_results(args)

    for task in range(0, train_set.total_n_classes // args["increment"]):
        # Setting current task's classes:
        train_set.set_classes_range(high=(task + 1) * args["increment"])
        test_set.set_classes_range(high=(task + 1) * args["increment"])

        model.set_task_info(
            task,
            train_set.total_n_classes,
            args["increment"],
            len(train_set),
            len(test_set)
        )

        model.before_task(train_loader, val_loader)
        model.train_task(train_loader, val_loader)
        model.after_task(train_loader)

        train_set.set_classes_range(high=(task + 1) * args["increment"])
        test_set.set_classes_range(high=(task + 1) * args["increment"])

        ypred, ytrue = model.eval_task(test_loader)
        acc_stats = utils.compute_accuracy(ypred, ytrue)
        print(acc_stats)
        results["results"].append(acc_stats)

    results_utils.save_results(results, args["name"])



def _set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
