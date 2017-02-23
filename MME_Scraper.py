import json
from os import listdir

class MME:
    _path_raw_dir = './raw_data/'
    _path_sql_out_file = './py_exports/sql_mme_drugs.txt'
    _path_out_file = './py_exports/mme_drugs.json'
    _path_skipped_file = './py_exports/skipped_drugs.json'
    _path_controlled_subs = './controlled_subs_v2.json'
    _controlled_subs = None

    def __init__(self):
        self._controlled_subs = json.load(open(self._path_controlled_subs, 'r'))
        _opiods = self._identify_opioids()
        _factored_opiods = self.assign_factors(_opiods)
        _cleaned_opiods = self.clean_ndc(_factored_opiods)

        json.dump(_cleaned_opiods, open(self._path_out_file, 'w'))
        self.sql_convert(_cleaned_opiods)

    def _identify_opioids(self):
        try:
            _path_raw_dir = self._path_raw_dir
            _controlled_subs = self._controlled_subs
            _path_skipped = self._path_skipped_file
            _results_dict = dict()
            _skipped_drugs = list()

            for _raw_file in listdir(_path_raw_dir):
                _path = '%s/%s' % (_path_raw_dir, _raw_file)
                raw = json.load(open(_path, 'r'))
                raw = raw['results']

                for _rcd in raw:
                    try:
                        for _subst in _rcd['openfda']['substance_name']:
                            for _drug in _controlled_subs:
                                if str(_subst).lower().startswith(_drug.lower()) or (' %s' % _drug.lower()) in str(_subst).lower():

                                    if _drug not in _results_dict:
                                        _results_dict[_drug] = dict()

                                    for _route in _rcd['openfda']['route']:
                                        if _route not in _results_dict[_drug]:
                                            _results_dict[_drug][_route] = {
                                                "openfda": [_rcd['openfda']]
                                            }
                                        else:
                                            _results_dict[_drug][_route]['openfda'].append(_rcd['openfda'])
                                    break
                    except Exception as err2:
                        _skipped_drugs.append(_rcd['openfda'])

            json.dump(_skipped_drugs, open(_path_skipped, 'w'))
            return _results_dict

        except Exception as err:
            print(err.args)
            raise err
            exit()

    def assign_factors(self, opiods_json):
        try:
            _controlled_subs = self._controlled_subs
            _mme_drugs = opiods_json

            for _drug in _mme_drugs:
                for _route in _mme_drugs[_drug]:

                    # fda routes exists, assign route specific factor
                    if type(_controlled_subs[_drug]['factor']) == dict:
                        if _route in _controlled_subs[_drug]['factor']:
                            _mme_drugs[_drug][_route]['factor'] = _controlled_subs[_drug]['factor'][_route]

                    else:
                        # else assign generic factor for all forms
                        _mme_drugs[_drug][_route]['factor'] = _controlled_subs[_drug]['factor']

            return _mme_drugs
        except Exception as err:
            print(err.args)
            raise err
            exit()

    def clean_ndc(self, opiods_json):
        try:
            _mme_ndc = opiods_json

            for _drug in _mme_ndc:
                for _route in _mme_ndc[_drug]:
                    _raw_ndc_set = set()
                    _clean_ndc_set = set()

                    for _rcd in _mme_ndc[_drug][_route]['openfda']:
                        for _ndc in _rcd['package_ndc']:
                            _raw_ndc_set.add(_ndc)

                    for _raw_ndc in _raw_ndc_set:
                        if _raw_ndc.find('-'):
                            _clean_ndc_set.add(self._convert_ndc(_raw_ndc))
                        else:
                            _clean_ndc_set.add(_raw_ndc)

                    _mme_ndc[_drug][_route]['clean_ndc'] = list(_clean_ndc_set)

            return _mme_ndc
        except Exception as err:
            print(err.args)
            raise err
            exit()

    def sql_convert(self, opiods_json):
        try:
            _path_out = self._path_sql_out_file
            _mme_drugs = opiods_json

            with open(_path_out, 'w') as _out:
                for _drug in _mme_drugs:
                    for _route in _mme_drugs[_drug]:
                        _factor = _mme_drugs[_drug][_route]['factor']
                        for _ndc in _mme_drugs[_drug][_route]['clean_ndc']:
                            _out.write('\t'.join([_drug, _route, _ndc, str(_factor)]))
                            _out.write('\n')
                _out.close()

        except Exception as err:
            print(err.args)
            raise err
            exit()

    @staticmethod
    def _convert_ndc(raw_ndc):
        """ FDA conversion of NDC to 11 char NDC"""
        try:
            _raw = raw_ndc.split('-')

            if len(_raw[0].strip()) < 5:
                _prefix = ''
                for _i in range(5 - len(_raw[0])):
                    _prefix += '0'

                _raw[0] = _prefix + _raw[0]

            if len(_raw[1].strip()) < 4:
                _prefix = ''
                for _i in range(4 - len(_raw[1])):
                    _prefix += '0'

                _raw[1] = _prefix + _raw[1]

            if len(_raw[2].strip()) < 2:
                _prefix = ''
                for _i in range(2 - len(_raw[2])):
                    _prefix += '0'

                _raw[2] = _prefix + _raw[2]

            return ''.join(_raw)
        except Exception as _err:
            print(_err)
            raise _err
            exit()



if __name__ == ('__main__'):
    MME()
