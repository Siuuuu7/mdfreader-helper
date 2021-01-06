# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 09:57:08 2020

@author: haoyang.yu
"""
import mdfreader as mdf
import pandas as pd
import numpy as np

class mdf_parser():
    '''
    mdfreader常用操作

    merge_to_pd : 将目标列拼接成带时间戳的DataFrame
    keyword_merge_to_pd : 用模糊变量名查询并拼接成带时间戳的DataFrame

    Parameters
    --------
    filename : dat/mdf文件名
    columns : 需要读取的通道名/缩写

    '''

    abbr_dict = dict()
    def __init__(self, filename, columns):
        self.filename = filename
        self.columns = columns

    # def _check_abbr_dict(self):
    #     # Create if abbr dictionary does not exist
    #     try:
    #         self.abbr_dict
    #     except NameError:
    #         self.abbr_dict = dict()

    def _change_abbr(self, abbr, col):
        # Add column name to the abbr dictionary
        # self._check_abbr_dict()
        self._rate_col(abbr, col)
        return 0

    def _find_name(self, all_cols, abbr, fill_nan=False):
        # Find full name of the abbr
        match_cols = [i for i in all_cols if abbr in i]
        if len(match_cols) == 0:
            #raise IndexError('[ERROR] No ' + abbr + ' in this file')
            new_abbr = input('[ERROR] No ' + abbr + ' in this file.'
                             'Enter another keyword or enter SKIP to skip: ')
            if new_abbr == 'SKIP':
                return 0
            else:
                return self._find_name(all_cols, new_abbr)
        elif len(match_cols) == 1:
            return match_cols[0]
        else:
            try:
                match = self._match_abbr_dict(abbr, match_cols)
                if match != 0:
                    return match
            except KeyError:
                pass
            print('[INFO] Multiple columns including "%s". Select from below' % abbr)
            for i in range(len(match_cols)):
                print(str(i) + ': ' + match_cols[i])
            num = self._input_num(match_cols)
            self._input_bool(abbr, match_cols[num])
            return match_cols[num]

    def _input_bool(self, abbr, col):
        # Whether the selected column used for all rest files
        hereditary = input('Use selected column for next files? y/n: ')
        if hereditary == 'y':
            print('Using %s in next files' % col)
            self._change_abbr(abbr, col)
        elif hereditary == 'n':
            pass
        else:
            print('[WARNING] Invalid input. Enter again')
            self._input_bool(abbr, col)

    def _input_num(self, match_cols):
        # Which column to use when multiple cols match the abbr
        raw_in = input('Enter the number: ')
        try:
            num = int(raw_in)
            print(num)
            if num < len(match_cols):
                print(num)
                return num
            else:
                print('[WARNING] Invalid Number. Enter again')
                return self._input_num(match_cols)
        except ValueError:
            print('Invalid input type. Enter again')
            return self._input_num(match_cols)

    def _match_abbr_dict(self, abbr, match_cols):
        # Create abbr dictionary
        for i in self.abbr_dict[abbr]:
            if i in match_cols:
                return i
        return 0

    def _merge_col(self, mdf_file, old_df, channel, key=False):
        # Merge the selected column to the DataFrame
        timer = mdf_file[channel]['master']
        new_column = mdf_file.return_pandas_dataframe(timer)[channel]
        if key:
            new_column.name = key
        try:
            new_df = pd.merge_asof(
                old_df,
                new_column,
                left_index=True, right_index=True, direction='nearest')
        except TypeError:  # first column, not good enough tbh
            return new_column
        return new_df

    def _rate_col(self, abbr, col):
        # Rate the selected column in the abbr dict
        # when former selected columns cannot be found in the current file

        # todo use defaultdict 
        try:
            self.abbr_dict[abbr]
            print([str(i) + ': ' + self.abbr_dict[abbr][i] for i in range(len(self.abbr_dict[abbr]))])
            print('Select priority')
            print('Where to insert? (Enter "1 + the largest number" or 9999'
                  'if this is the least wanted variable in the dictionary above)')
            rate = input('Enter Number: ')
            try:
                self.abbr_dict[abbr].insert(int(rate), col)
            except ValueError:
                print('Invalid input type. Enter again')
                return self._rate_col(abbr, col)
            return 0
        except KeyError:
            self.abbr_dict[abbr] = [col]
            return 0

    def _find_var_merge(self, file, possible_vars, all_cols, merged_df, channel, key):
        for var in possible_vars:
            if channel:
                var['name'] = var['name'] + ':' + channel
            if var['name'] in all_cols:
                return self._merge_col(file, merged_df, var['name'], key), var['variable_id']
        nan_df = pd.DataFrame(np.nan, index=merged_df.index, columns=[key], dtype='float')
        add_zero_df = pd.concat([merged_df, nan_df], axis=1)
        return add_zero_df, -1

    def signal_list_merge_to_pd(self, channel, ids):
        '''
        Find the names of the wanted signals in the  
        current file and merge them to the dataframe

        Returns
        -------
        merged_df : Pandas DataFrame
            DataFrame with all the info from the given channels.
        '''
        filename = self.filename
        var_dict = self.columns
        file = mdf.Mdf(filename)
        all_cols = file.keys()
        merged_df = pd.DataFrame()
        for key in var_dict.keys():
            possible_vars = var_dict[key]
            merged_df, var_id = self._find_var_merge(file, possible_vars, all_cols, merged_df, channel, key)
            if var_id != -1:
                ids[key] = var_id
        return merged_df, ids


    def merge_to_pd(self):
        '''
        Merge channel data to the dataframe

        Returns
        -------
        merged_df : Pandas DataFrame
            DataFrame with all the info from the given channels.
        '''

        filename = self.filename
        file = mdf.Mdf(filename)
        origin_cols = self.columns
        merged_df = pd.DataFrame()
        for channel in origin_cols:
            merged_df = self._merge_col(file, merged_df, channel)
        return merged_df

    def keyword_merge_to_pd(self):
        '''
        Find full name according to the keywords and merge the data to the dataframe

        Returns
        -------
        merged_df : Pandas DataFrame
            DataFrame with all the info from the given channels.
        '''

        filename = self.filename
        file = mdf.Mdf(filename)
        print('Parsing file: ' + filename)
        abbr_cols = self.columns
        merged_df = pd.DataFrame()
        all_cols = file.keys()
        for abbr in abbr_cols:
            channel = self._find_name(all_cols, abbr)
            if channel == 0:
                print('Nan col Warning')
                nan_df = pd.DataFrame(np.nan, index=merged_df.index, columns=[abbr], dtype='float')
                merged_df = pd.concat([merged_df, nan_df], axis=1)
            else:
                merged_df = self._merge_col(file, merged_df, channel)
        merged_df.columns = abbr_cols
        return merged_df


class pd_parser():  # based on pandas dataframe
    '''
    DataFrame常用操作
    trace_back : 添加特征前序时间序列
    add_MeanVar ：添加特征前序时间的均值和方差
    resample : 用采样时间内的均值重采样
    initialize : 初始化，为每一行添加上一时刻的标签值
    add_col : 添加新列

    Parameters
    --------
    content : DataFrame
    label : Targeted column name
    '''

    def __init__(self, content, label=[]):
        '''
        Parameters
        ----------
        content : Pandas DataFrame
            DF to be parsed
        label : string, optional
            Target label. The default is empty list.
        '''

        self.content = content
        self.label = label

    def trace_back(self, back_num=5, columns=None):
        '''
        Parameters
        ----------
        back_num : int, optional
            Number of rows to trace back. The default is 5.
        columns : list of strings, optional
            Column names to trace back. The default is None.

        Returns
        -------
        _df : Pandas DataFrame,
            DataFrame with information from previous columns
        '''

        content = self.content
        if columns is None:
            old_cols = content.columns.drop(self.label)
        else:
            old_cols = columns
        _df = content.drop(content.index[0:back_num]).reset_index(drop=True)
        for k in range(0, back_num, 1):
            back_cols = [j + '-' + str(1 + k) for j in old_cols]
            last_info = content[old_cols][(back_num - 1 - k):(-1 - k)].reset_index(drop=True)
            last_info.columns = back_cols
            _df = pd.concat([_df, last_info], sort=True, axis=1)

        return _df

    def add_MeanVar(self, back_num=5, columns=None, methods=[i + 1 for i in range(7)]):
        '''
        Parameters
        ----------
        back_num : int, optional
            Number of rows to trace back. The default is 5.
        columns : list of strings, optional
            Column names to trace back. The default is None, indicating using all columns.
        methods : list of int, optional. The default is [1,2,...,7], indicating using all methods.
            Added features:
                1 : mean
                2 : variance
                3 : standard deviation
                4 : quantile 0.25
                5 : quantile 0.75
                6 : kurtosis
                7 : skewing
        Returns
        -------
        _df : Pandas DataFrame
            DataFrame with information from previous columns
        '''

        content = self.content
        if columns is None:
            old_cols = content.columns.drop(self.label)
        else:
            old_cols = columns
        add_col = []
        add_df = pd.DataFrame()
        if 1 in methods:
            add_col.extend([i + '_mean' for i in old_cols])
            add_df = pd.concat([
                add_df, content[old_cols].rolling(back_num).mean()], axis=1)
        if 2 in methods:
            add_col.extend([i + '_var' for i in old_cols])
            add_df = pd.concat([
                add_df, content[old_cols].rolling(back_num).var()], axis=1)
        if 3 in methods:
            add_col.extend([i + '_std' for i in old_cols])
            add_df = pd.concat([
                add_df, content[old_cols].rolling(back_num).std()], axis=1)

        if 4 in methods:
            add_col.extend([i + '_q25' for i in old_cols])
            add_df = pd.concat([
                add_df, content[old_cols].rolling(back_num).quantile(
                    0.25, interpolation='midpoint')], axis=1)
        if 5 in methods:
            add_col.extend([i + '_q75' for i in old_cols])
            add_df = pd.concat([
                add_df, content[old_cols].rolling(back_num).quantile(
                    0.75, interpolation='midpoint')], axis=1)
        if 6 in methods:
            add_col.extend([i + '_skw' for i in old_cols])
            skew = content[old_cols].rolling(back_num).skew()
            if skew.isna().sum().sum() > back_num - 1:
                raise ValueError('[Error]Skewness reaches inf, please use other methods or'
                                 'resample the data')
            add_df = pd.concat([add_df, skew], axis=1)
        if 7 in methods:
            add_col.extend([i + '_krt' for i in old_cols])
            kurt = content[old_cols].rolling(back_num).kurt()
            if kurt.isna().sum().sum() > back_num - 1:
                raise ValueError('[Error]Kurtosis reaches inf, please use other methods or'
                                 'resample the data')
            add_df = pd.concat([add_df, kurt], axis=1)
        add_df.columns = add_col
        _df = pd.concat([add_df, content], axis=1).reset_index(drop=True)
        _df = _df.iloc[back_num - 1:].reset_index(drop=True)

        return _df

    def resample(self, rate):
        '''
        Parameters
        ----------
        rate : int
            Resample rate. The default is 100

        Returns
        -------
        _df : Pandas DataFrame
            Resampled DataFrame
        '''

        content = self.content
        new_index = content.index[::rate]
        ind = pd.date_range('1/1/2000', periods=len(content), freq='T')
        content.index = ind
        _df = content.resample(str(rate) + 'T').mean()
        _df.index = new_index

        return _df

    def initialize(self, back_num=1, add_all=False):
        '''
        Parameters
        ----------
        back_num : int, optional
            Number of rows to trace back for initialization. The default is 1.
        add_all : bool, optional
            True, if all of the last (back_num) labels are added as new features
            False, if only the last (back_num)th label is added as a new feature

        Returns
        -------
        _df : Pandas DataFrame
            DataFrame with the label from the last (back_num)th row/ (back_num) rows
        '''

        content = self.content
        label = self.label
        _df = content.drop(content.index[:back_num])
        ind = _df.index
        _df = _df.reset_index(drop=True)
        for k in range(0, back_num, 1):
            if add_all is False and k != back_num - 1:
                continue
            back_col = label + '_' + str(1 + k)
            last_label = content[label][(back_num - 1 - k):(-1 - k)].reset_index(drop=True)
            last_label.name = back_col
            _df = pd.concat([_df, last_label], sort=True, axis=1)
        _df.index = ind
        return _df

    def add_col(self, *args, method='minus', time=10):
        # integrate add_meanvar in the future
        df = self.content
        args_num = len(args)
        if args_num < 1:
            raise KeyError('add_col() needs at least one column')
        elif args_num == 1:
            col1 = args[0]
            if method == 'max':
                df[col1 + 'max'] = df[col1].rolling(time).max()
            elif method == 'min':
                df[col1 + 'max'] = df[col1].rolling(time).min()
            elif method == 'sum':
                df[col1 + 'max'] = df[col1].rolling(time).sum()
            df = df.fillna(0)  # temporary...
        elif args_num == 2:
            col1 = args[0]
            col2 = args[1]
            if method == 'minus':
                df[col1 + '-' + col2] = df[col1] - df[col2]
            elif method == 'plus':
                df[col1 + '-' + col2] = df[col1] + df[col2]
            else:
                raise KeyError('Invalid method for 2 columns')
        else:
            if method == 'sum':
                df[args] = df[list(args)].sum(axis=1)
            else:
                raise KeyError('Invalid method for %d columns' % args_num)
        return df


if __name__ == '__main__':
    import glob
    abbrs = ['n', 'wMCT', 'MCT_', 'ISC']  # 区分大小写，避免使用同样缩写的两个变量
    dat_cols = ['ISC_n:CCP2', 'MCT_TrqMech:CCP2']
    mdf_cols = ['ISC_n', 'MCT_TrqEm', 'ISC_TempDBCInvCoolObsvr', 'MCT_IsdDes', 'ISC_Isq']
    var_list = [[{'variable_id': 28,
   'name': 'agCtrlDif.Irv_rbe_CddRslvr_100us.rbe_CddRslvr'}],
 [{'variable_id': 30,
   'name': 'iPhaSum.Irv_rbe_CddMonFctIPha_10ms.rbe_CddMonFctIPha'}],
 [{'variable_id': 9, 'name': 'nEmFild10ms.Irv_rbe_CddRslvr_2ms.rbe_CddRslvr'},
  {'variable_id': 10,
   'name': 'nEmFild100ms.Rec_10ms_Fild.pp_rbe_CddAgEm_10ms_Fild.rbe_CddRslvr'},
  {'variable_id': 13, 'name': 'nEm.Irv_rbe_CddRslvr_100us.rbe_CddRslvr'},
  {'variable_id': 53, 'name': 'ISC_n:CCP2'},
  {'variable_id': 18,
   'name': 'nEmFild100ms.Rec_10ms_Fild.rp_rbe_CddAgEm_10ms_Fild.rbe_TMdlEm'}],
 [{'variable_id': 14, 'name': 'MCT_TrqMech'},
  {'variable_id': 52, 'name': 'MCT_TrqMech:CCP2'},
  {'variable_id': 15,
   'name': 'tqMecl.Rec_10ms_Com.pp_rbe_Cif_10ms_Com.rbe_Cif'},
  {'variable_id': 16, 'name': 'tqMecl.Irv_rbe_MctPsm_2ms.rbe_MctPsm'},
  {'variable_id': 17,
   'name': 'tqMeclFild100ms.MdlTqMeclFil.MdlTq.Mdl.Mai.rbe_MctPsm'}],
 [{'variable_id': 44,
   'name': 'tAcRail.Rec_100ms.rp_rbe_TMdlRail_100ms.rbe_DernIvtr'}],
 [{'variable_id': 45,
   'name': 'tCap.Rec_100ms.pp_rbe_TMdlCap_100ms.rbe_TMdlCap'},
  {'variable_id': 46,
   'name': 'tCap.Rec_100ms.rp_rbe_TMdlCap_100ms.rbe_CddTCap'},
  {'variable_id': 47,
   'name': 'tCap.Rec_100ms.rp_rbe_TMdlCap_100ms.rbe_DernIvtr'},
  {'variable_id': 48,
   'name': 'tCapSnsrMdl.Rec_100ms.pp_rbe_TMdlCap_100ms.rbe_TMdlCap'}],
 [{'variable_id': 32,
   'name': 'tCooltIvtr.Rec_10ms.rp_rbe_TMdlIvtr_10ms.rbe_DernIvtr'},
  {'variable_id': 33,
   'name': 'tCooltIvtrFild100ms.Rec_10ms_Fild.rp_rbe_TMdlIvtr_10ms_Fild.rbe_TMdlEm'}],
 [{'variable_id': 34,
   'name': 'tCooltInCooltObsvr.TCooltObsvr.Mai.rbe_TMdlIvtr'}],
 [{'variable_id': 31,
   'name': 'tCooltOutCooltObsvr.TCooltObsvr.Mai.rbe_TMdlIvtr'}],
 [{'variable_id': 49,
   'name': 'tDcRail.Rec_100ms.rp_rbe_TMdlRail_100ms.rbe_DernIvtr'}],
 [{'variable_id': 35,
   'name': 'tSnsrPwrModlPha1.Irv_rbe_CddHvMcu_2ms.rbe_CddHvMcu'},
  {'variable_id': 36,
   'name': 'tSnsrPwrModlPha1Fild100ms.Rec_10ms_Fild.rp_rbe_CddHvMcu_10ms_Fild.rbe_TMdlIvtr'},
  {'variable_id': 37,
   'name': 'tSnsrPwrModlPha1Fild10ms.Irv_rbe_CddHvMcu_2ms.rbe_CddHvMcu'}],
 [{'variable_id': 38,
   'name': 'tSnsrPwrModlPha2.Irv_rbe_CddHvMcu_2ms.rbe_CddHvMcu'},
  {'variable_id': 39,
   'name': 'tSnsrPwrModlPha2Fild100ms.Rec_10ms_Fild.rp_rbe_CddHvMcu_10ms_Fild.rbe_TMdlIvtr'},
  {'variable_id': 40,
   'name': 'tSnsrPwrModlPha2Fild10ms.Irv_rbe_CddHvMcu_2ms.rbe_CddHvMcu'}],
 [{'variable_id': 41,
   'name': 'tSnsrPwrModlPha3.Irv_rbe_CddHvMcu_2ms.rbe_CddHvMcu'},
  {'variable_id': 42,
   'name': 'tSnsrPwrModlPha3Fild100ms.Rec_10ms_Fild.rp_rbe_CddHvMcu_10ms_Fild.rbe_TMdlIvtr'},
  {'variable_id': 43,
   'name': 'tSnsrPwrModlPha3Fild10ms.Irv_rbe_CddHvMcu_2ms.rbe_CddHvMcu'}],
 [{'variable_id': 50, 'name': 'tOilGbxMdl.Irv_rbe_TMdlGbx_100ms.rbe_TMdlGbx'}],
 [{'variable_id': 23,
   'name': 'tRotor.Rec_10ms_Com.pp_rbe_Cif_10ms_Com.rbe_Cif'},
  {'variable_id': 24, 'name': 'tRotor.MdlTTherm.MdlT.Mdl.Mai.rbe_MctPsm'}],
 [{'variable_id': 27, 'name': 'tRotorOld.MdlTTherm.Mai.rbe_TMdlEm'}],
 [{'variable_id': 19, 'name': 'tEmSnsr.Irv_rbe_CddTEm_2ms.rbe_CddTEm'},
  {'variable_id': 20,
   'name': 'tEmSnsrFild100ms.Rec_10ms_Fild.pp_rbe_CddTEm_10ms_Fild.rbe_CddTEm'},
  {'variable_id': 21, 'name': 'tEmSnsrFild10ms.Irv_rbe_CddTEm_2ms.rbe_CddTEm'},
  {'variable_id': 22,
   'name': 'tEmSnsrFild100ms.Rec_10ms_Fild.rp_rbe_CddTEm_10ms_Fild.rbe_TMdlEm'}]]
    filenames = glob.glob('./dat/idc/*.dat')  # 二选一
    #filenames = glob.glob('../../tools/mdf/ru/*.mf4')   # 二选一，未来版本可以尝试两种格式混在一起
    df = pd.DataFrame()
    for file in filenames:
        out = mdf_parser(file, abbrs).keyword_merge_to_pd()
        #out, var_ids = mdf_parser(file, var_list).signal_list_merge_to_pd()
        #out = mdf_parser(file, dat_cols).merge_to_pd()
        #out = mdf_parser(file, mdf_cols).merge_to_pd()
        '''
        RENAMING COLUMNS HIGHLY RECOMMENDED HERE
        ESPECIALLY WHEN ONE PHYSICAL QUANTITY CORRESPONDS TO MULTI NAMES IN ORIGINAL FILES
        '''
        #df.columns = ['Speed', 'Torque', 'blabla1', 'blabla2']
        df = pd.concat([df, out], axis=0)
    raw_df = df.copy()
    # DataFrame resampling with the mean value
    rsp_df = pd_parser(df).resample(rate=100)
    raw_rsp_df = rsp_df.copy()
    label = raw_df.columns[1]
    back_cols = raw_df.columns[2:3]  # must be a list

    # Add mean&variance of the back_cols in the last 5 timesteps
    mv_df = pd_parser(rsp_df, label).add_MeanVar(back_num=5, columns=back_cols)

    # Add all of the back_cols in the last 1 timestep
    back_df = pd_parser(rsp_df, label).trace_back(back_num=1)

    # Add label from the last row
    init_df = pd_parser(rsp_df, label).initialize(back_num=1)
