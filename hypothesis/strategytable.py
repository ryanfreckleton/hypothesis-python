from hypothesis.internal.specmapper import SpecificationMapper
import hypothesis.searchstrategy as strat
from six import text_type, binary_type
import hypothesis.descriptors as descriptors


def convert_strategy(fn):
    if isinstance(fn, strat.SearchStrategy):
        return lambda strategies, descriptor: fn
    return fn


def strategy_for(typ):
    def accept_function(fn):
        StrategyTable.default().define_specification_for(
            typ, convert_strategy(fn))
        return fn
    return accept_function


def strategy_for_instances(typ):
    def accept_function(fn):
        StrategyTable.default().define_specification_for_instances(
            typ, convert_strategy(fn))
        return fn
    return accept_function


class StrategyTable(SpecificationMapper):
    def strategy(self, descriptor):
        return self.specification_for(descriptor)

    def missing_specification(self, descriptor):
        if isinstance(descriptor, strat.SearchStrategy):
            return descriptor
        else:
            return SpecificationMapper.missing_specification(self, descriptor)


strategy_for(int)(strat.IntStrategy())
strategy_for(bool)(strat.BoolStrategy())


@strategy_for(text_type)
def define_text_type_strategy(strategies, descriptor):
    child = strategies.new_child_mapper()
    c = strat.OneCharStringStrategy()
    child.define_specification_for(
        text_type, lambda x, y: c)
    list_of_strings = child.strategy([text_type])
    return strat.StringStrategy(list_of_strings)


@strategy_for(float)
def define_float_strategy(strategies, descriptor):
    return (
        strat.GaussianFloatStrategy() |
        strat.BoundedFloatStrategy() |
        strat.ExponentialFloatStrategy())


@strategy_for(binary_type)
def define_binary_strategy(strategies, descriptor):
    return strat.BinaryStringStrategy(
        strategy=strategies.strategy(text_type),
        descriptor=binary_type,
    )


@strategy_for_instances(set)
def define_set_strategy(strategies, descriptor):
    return strat.SetStrategy(strategies.strategy(list(descriptor)))


@strategy_for(complex)
def define_complex_strategy(strategies, descriptor):
    return strat.ComplexStrategy(strategies.strategy((float, float)))


@strategy_for_instances(descriptors.Just)
def define_just_strategy(strategies, descriptor):
    return strat.JustStrategy(descriptor.value)


@strategy_for_instances(list)
def define_list_strategy(strategies, descriptor):
    return strat.ListStrategy(list(map(strategies.strategy, descriptor)))


@strategy_for_instances(tuple)
def define_tuple_strategy(strategies, descriptor):
    return strat.TupleStrategy(
        tuple(map(strategies.strategy, descriptor)),
        tuple_type=type(descriptor)
    )


@strategy_for_instances(dict)
def define_dict_strategy(strategies, descriptor):
    strategy_dict = {}
    for k, v in descriptor.items():
        strategy_dict[k] = strategies.strategy(v)
    return strat.FixedKeysDictStrategy(strategy_dict)


@strategy_for_instances(descriptors.OneOf)
def define_one_of_strategy(strategies, descriptor):
    return strat.OneOfStrategy(map(strategies.strategy, descriptor.elements))
