from audition.distance_from_best import DistanceFromBestTable
from audition.thresholding import ModelGroupThresholder
import testing.postgresql
from sqlalchemy import create_engine
from results_schema.factories import ModelGroupFactory, init_engine, session
from catwalk.db import ensure_db
from unittest import TestCase


class ModelGroupThresholderTest(TestCase):
    metric_filters = [
        {
            'metric': 'precision@',
            'metric_param': '100_abs',
            'max_below_best': 0.2,
            'min_value': 0.4,
        },
        {
            'metric': 'recall@',
            'metric_param': '100_abs',
            'max_below_best': 0.2,
            'min_value': 0.4,
        }
    ]

    def setup_data(self, engine):
        ensure_db(engine)
        init_engine(engine)
        ModelGroupFactory(model_group_id=1, model_type='modelType1')
        ModelGroupFactory(model_group_id=2, model_type='modelType2')
        ModelGroupFactory(model_group_id=3, model_type='modelType3')
        ModelGroupFactory(model_group_id=4, model_type='modelType4')
        ModelGroupFactory(model_group_id=5, model_type='modelType5')
        session.commit()
        distance_table = DistanceFromBestTable(
            db_engine=engine,
            models_table='models',
            distance_table='dist_table'
        )
        distance_table._create()
        distance_rows = [
            # 2014: model group 1 should pass both close and min checks
            (1, 1, '2014-01-01', 'precision@', '100_abs', 0.5, 0.0, 0.38),
            (1, 1, '2014-01-01', 'recall@', '100_abs', 0.5, 0.0, 0.38),
            # 2015: model group 1 should not pass close check
            (1, 2, '2015-01-01', 'precision@', '100_abs', 0.5, 0.38, 0.0),
            (1, 2, '2015-01-01', 'recall@', '100_abs', 0.5, 0.38, 0.0),
            (1, 3, '2016-01-01', 'precision@', '100_abs', 0.46, 0.0, 0.11),
            (1, 3, '2016-01-01', 'recall@', '100_abs', 0.46, 0.0, 0.11),
            # 2014: model group 2 should not pass min check
            (2, 4, '2014-01-01', 'precision@', '100_abs', 0.39, 0.11, 0.5),
            (2, 4, '2014-01-01', 'recall@', '100_abs', 0.5, 0.0, 0.38),
            # 2015: model group 2 should pass both checks
            (2, 5, '2015-01-01', 'precision@', '100_abs', 0.69, 0.19, 0.12),
            (2, 5, '2015-01-01', 'recall@', '100_abs', 0.69, 0.19, 0.0),
            (2, 6, '2016-01-01', 'precision@', '100_abs', 0.34, 0.12, 0.11),
            (2, 6, '2016-01-01', 'recall@', '100_abs', 0.46, 0.0, 0.11),
            # model group 3 not included in this round
            (3, 7, '2014-01-01', 'precision@', '100_abs', 0.28, 0.22, 0.0),
            (3, 7, '2014-01-01', 'recall@', '100_abs', 0.5, 0.0, 0.38),
            (3, 8, '2015-01-01', 'precision@', '100_abs', 0.88, 0.0, 0.02),
            (3, 8, '2015-01-01', 'recall@', '100_abs', 0.5, 0.38, 0.0),
            (3, 9, '2016-01-01', 'precision@', '100_abs', 0.44, 0.02, 0.11),
            (3, 9, '2016-01-01', 'recall@', '100_abs', 0.46, 0.0, 0.11),
            # 2014: model group 4 should not pass any checks
            (4, 10, '2014-01-01', 'precision@', '100_abs', 0.29, 0.21, 0.21),
            (4, 10, '2014-01-01', 'recall@', '100_abs', 0.5, 0.0, 0.38),
            # 2015: model group 4 should not pass close check
            (4, 11, '2015-01-01', 'precision@', '100_abs', 0.67, 0.21, 0.21),
            (4, 11, '2015-01-01', 'recall@', '100_abs', 0.5, 0.38, 0.0),
            (4, 12, '2016-01-01', 'precision@', '100_abs', 0.25, 0.21, 0.21),
            (4, 12, '2016-01-01', 'recall@', '100_abs', 0.46, 0.0, 0.11),
            # 2014: model group 5 should not pass because precision is good but not recall
            (5, 13, '2014-01-01', 'precision@', '100_abs', 0.5, 0.0, 0.38),
            (5, 13, '2014-01-01', 'recall@', '100_abs', 0.3, 0.2, 0.38),
            # 2015: model group 5 should not pass because precision is good but not recall
            (5, 14, '2015-01-01', 'precision@', '100_abs', 0.5, 0.38, 0.0),
            (5, 14, '2015-01-01', 'recall@', '100_abs', 0.3, 0.58, 0.0),
            (5, 15, '2016-01-01', 'precision@', '100_abs', 0.46, 0.0, 0.11),
            (5, 16, '2016-01-01', 'recall@', '100_abs', 0.3, 0.16, 0.11),
        ]
        for dist_row in distance_rows:
            engine.execute(
                'insert into dist_table values (%s, %s, %s, %s, %s, %s, %s, %s)',
                dist_row
            )
        thresholder = ModelGroupThresholder(
            db_engine=engine,
            distance_from_best_table=distance_table,
            train_end_times=['2014-01-01', '2015-01-01'],
            initial_model_group_ids=[1, 2, 4, 5]
        )
        return thresholder

    def test_thresholder_2014_close(self):
        with testing.postgresql.Postgresql() as postgresql:
            engine = create_engine(postgresql.url())
            thresholder = self.setup_data(engine)
            thresholder._metric_filters = self.metric_filters
            assert thresholder.model_groups_close_to_best_as_of(
                train_end_time='2014-01-01',
            ) == set([1, 2])

    def test_thresholder_2015_close(self):
        with testing.postgresql.Postgresql() as postgresql:
            engine = create_engine(postgresql.url())
            thresholder = self.setup_data(engine)
            thresholder._metric_filters = self.metric_filters
            assert thresholder.model_groups_close_to_best_as_of(
                train_end_time='2015-01-01',
            ) == set([2])

    def test_thresholder_2014_min(self):
        with testing.postgresql.Postgresql() as postgresql:
            engine = create_engine(postgresql.url())
            thresholder = self.setup_data(engine)
            thresholder._metric_filters = self.metric_filters
            assert thresholder.model_groups_above_min_as_of(
                train_end_time='2014-01-01',
            ) == set([1])

    def test_thresholder_2015_min(self):
        with testing.postgresql.Postgresql() as postgresql:
            engine = create_engine(postgresql.url())
            thresholder = self.setup_data(engine)
            thresholder._metric_filters = self.metric_filters
            assert thresholder.model_groups_above_min_as_of(
                train_end_time='2015-01-01',
            ) == set([1, 2, 4])

    def test_thresholder_all_rules(self):
        with testing.postgresql.Postgresql() as postgresql:
            engine = create_engine(postgresql.url())
            thresholder = self.setup_data(engine)
            thresholder._metric_filters = self.metric_filters
            # The multi-date version of this function should have
            # the mins ANDed together and the closes ORed together
            assert thresholder.model_groups_passing_rules() == set([1])

    def test_update_filters(self):
        with testing.postgresql.Postgresql() as postgresql:
            engine = create_engine(postgresql.url())
            thresholder = self.setup_data(engine)
            assert thresholder.model_group_ids == [1, 2, 4, 5]
            thresholder.update_filters([
                {
                    'metric': 'precision@',
                    'metric_param': '100_abs',
                    'max_below_best': 0.2,
                    'min_value': 0.4,
                },
                {
                    'metric': 'recall@',
                    'metric_param': '100_abs',
                    'max_below_best': 0.2,
                    'min_value': 0.4,
                }
            ])
            assert thresholder.model_group_ids == set([1])
