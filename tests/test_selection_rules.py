from audition.selection_rules import best_metric_value, best_average_value, most_frequent_best_dist, best_average_two_metrics
import pandas


def test_best_metric_value():
    df = pandas.DataFrame.from_dict({
        'model_group_id': ['1', '2', '1', '2'],
        'model_id': ['1', '2', '3', '4'],
        'train_end_time': ['2011-01-01', '2011-01-01', '2012-01-01', '2012-01-01'],
        'metric': ['precision@', 'precision@', 'precision@', 'precision@'],
        'parameter': ['100_abs', '100_abs', '100_abs', '100_abs'],
        'dist_from_abs_worst': [0.5, 0.4, 0.6, 0.7],
        'dist_from_best_case': [0.0, 0.1, 0.1, 0.0],
    })

    assert best_metric_value(df, '2011-01-01', 'precision@', '100_abs') == '1'
    assert best_metric_value(df, '2012-01-01', 'precision@', '100_abs') == '2'


def test_best_average_value():
    df = pandas.DataFrame.from_dict({
        'model_group_id': ['1', '2', '1', '2', '1', '2'],
        'model_id': ['1', '2', '3', '4', '5', '6'],
        'train_end_time': ['2011-01-01', '2011-01-01', '2012-01-01', '2012-01-01', '2013-01-01', '2013-01-01'],
        'metric': ['precision@', 'precision@', 'precision@', 'precision@', 'precision@', 'precision@'],
        'parameter': ['100_abs', '100_abs', '100_abs', '100_abs', '100_abs', '100_abs'],
        'dist_from_abs_worst': [0.5, 0.4, 0.6, 0.69, 0.6, 0.62],
        'dist_from_best_case': [0.0, 0.1, 0.1, 0.0, 0.02, 0.0],
    })

    assert best_average_value(df, '2013-01-01', 'precision@', '100_abs') == '2'


def test_most_frequent_best_dist():
    df = pandas.DataFrame.from_dict({
        'model_group_id': ['1', '2', '1', '2', '1', '2'],
        'model_id': ['1', '2', '3', '4', '5', '6'],
        'train_end_time': ['2011-01-01', '2011-01-01', '2012-01-01', '2012-01-01', '2013-01-01', '2013-01-01'],
        'metric': ['precision@', 'precision@', 'precision@', 'precision@', 'precision@', 'precision@'],
        'parameter': ['100_abs', '100_abs', '100_abs', '100_abs', '100_abs', '100_abs'],
        'dist_from_abs_worst': [0.5, 0.4, 0.6, 0.69, 0.6, 0.62],
        'dist_from_best_case': [0.0, 0.1, 0.1, 0.0, 0.02, 0.0],
    })

    assert most_frequent_best_dist(df, '2013-01-01', 'precision@', '100_abs', 0.01) == '2'



def test_best_average_two_metrics():
    df = pandas.DataFrame.from_dict({
        'model_group_id': ['1', '1', '2', '2', '1', '1', '2', '2'], 
        'model_id': ['1', '1', '2', '2', '3', '3', '4', '4'],
        'train_end_time': ['2011-01-01', '2011-01-01', '2011-01-01', '2011-01-01', '2012-01-01', '2012-01-01', '2012-01-01', '2012-01-01'],
        'metric': ['precision@', 'recall@', 'precision@', 'recall@', 'precision@', 'recall@', 'precision@', 'recall@'],
        'parameter': ['100_abs', '100_abs', '100_abs', '100_abs', '100_abs', '100_abs', '100_abs', '100_abs'],
        'dist_from_abs_worst': [0.6, 0.4, 0.4, 0.6, 0.5, 0.5, 0.4, 0.5],
        'dist_from_best_case': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    })

    assert best_average_two_metrics(df, '2013-01-01', 'precision@', '100_abs', 'recall@', '100_abs', 0.5) == '1'
    assert best_average_two_metrics(df, '2013-01-01', 'precision@', '100_abs', 'recall@', '100_abs', 0.1) == '2'
