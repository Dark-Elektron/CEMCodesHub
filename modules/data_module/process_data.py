import json
import os

from scipy.optimize import fsolve
import numpy as np
import pandas as pd
from utils.file_reader import FileReader
fr = FileReader()

class ProcessData:
    def __init__(self):
        pass

    def weed(self, d):
        wed_dict = {}
        problem_keys = []
        new_key = 0
        for key, val in d.items():
            A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp = val['MC'][0], val['MC'][1], val['MC'][2], val['MC'][3], val['MC'][4], val['MC'][5], val['MC'][6], 0
            A_le, B_le, a_le, b_le, Ri_le, L_le, Req_le, L_bp = val['LC'][0], val['LC'][1], val['LC'][2], val['LC'][3], val['LC'][4], val['LC'][5], val['LC'][6], 0
            A_re, B_re, a_re, b_re, Ri_re, L_re, Req_re, L_bp = val['RC'][0], val['RC'][1], val['RC'][2], val['RC'][3], val['RC'][4], val['RC'][5], val['RC'][6], 0

            alpha_mc = self._calculate_alpha(A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp)
            alpha_lc = self._calculate_alpha(A_le, B_le, a_le, b_le, Ri_le, L_le, Req_le, L_bp)
            alpha_rc = self._calculate_alpha(A_re, B_re, a_re, b_re, Ri_re, L_re, Req_re, L_bp)

            if (91 <= alpha_mc <= 180) and (91 <= alpha_lc <= 180) and (91 <= alpha_rc <= 180) and (400.29 < val['FREQ'] < 401.29):

                wed_dict[new_key] = {'MC': [], 'LC': [], 'RC': [], 'BP': 0, 'FREQ': 0}

                # update save new
                wed_dict[new_key]['MC'] = [A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m]
                wed_dict[new_key]['LC'] = [A_le, B_le, a_le, b_le, Ri_le, L_le, Req_le]
                wed_dict[new_key]['RC'] = [A_re, B_re, a_re, b_re, Ri_re, L_re, Req_re]
                wed_dict[new_key]['BP'] = 'both'
                wed_dict[new_key]['FREQ'] = val['FREQ']

                new_key += 1
            else:
                problem_keys.append(key)

        return wed_dict, problem_keys

    def weed_maintain_key(self, d):
        wed_dict = {}
        problem_keys = []
        for key, val in d.items():
            A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp = val['MC'][0], val['MC'][1], val['MC'][2], val['MC'][3], val['MC'][4], val['MC'][5], val['MC'][6], 0
            A_le, B_le, a_le, b_le, Ri_le, L_le, Req_le, L_bp = val['LC'][0], val['LC'][1], val['LC'][2], val['LC'][3], val['LC'][4], val['LC'][5], val['LC'][6], 0
            A_re, B_re, a_re, b_re, Ri_re, L_re, Req_re, L_bp = val['RC'][0], val['RC'][1], val['RC'][2], val['RC'][3], val['RC'][4], val['RC'][5], val['RC'][6], 0

            alpha_mc = self._calculate_alpha(A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp)
            alpha_lc = self._calculate_alpha(A_le, B_le, a_le, b_le, Ri_le, L_le, Req_le, L_bp)
            alpha_rc = self._calculate_alpha(A_re, B_re, a_re, b_re, Ri_re, L_re, Req_re, L_bp)

            if (91 <= alpha_mc <= 180) and (91 <= alpha_lc <= 180) and (91 <= alpha_rc <= 180) and (400.29 < val['FREQ'] < 401.29):

                wed_dict[key] = {'MC': [], 'LC': [], 'RC': [], 'BP': 0, 'FREQ': 0}

                # update save new
                wed_dict[key]['MC'] = [A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m]
                wed_dict[key]['LC'] = [A_le, B_le, a_le, b_le, Ri_le, L_le, Req_le]
                wed_dict[key]['RC'] = [A_re, B_re, a_re, b_re, Ri_re, L_re, Req_re]
                wed_dict[key]['BP'] = 'both'
                wed_dict[key]['FREQ'] = val['FREQ']

            else:
                problem_keys.append(key)

        return wed_dict, problem_keys

    def combine_results(self, dir1, dir2, save_excel='recent_save'):

        d_FM = fr.excel_reader(dir1)
        d_HOM = fr.excel_reader(dir2)
        d_FM = d_FM['Sheet1']
        d_HOM = d_HOM['Sheet1']
        # print(d_HOM.iloc[0])

        ob_FM_key_align_dict, ob_HOM_key_align_dict = {}, {}
        for key, val in d_FM.iterrows():
            ob_FM_key_align_dict[int(val['key'])] = list(val)[2:]

        for key, val in d_HOM.iterrows():
            ob_HOM_key_align_dict[int(val['key'])] = list(val)[2:]

        # print(ob_FM_key_align_dict)
        # print()
        # print(ob_HOM_key_align_dict)

        save_new = {'key': [], 'A': [], 'B': [], 'a': [], 'b': [], 'Ri': [], 'L': [], 'Req': [], 'alpha': [],
                    'E_stored': [], 'Rsh': [], 'Q': [], 'Epk': [], 'Hpk': [], 'Eacc': [],
                    'Rsh/Q': [], 'Epk/Eacc': [], 'Bpk/Eacc': [], 'kcc': [],
                    'k_loss_M0': [], 'k_loss_long': [], 'k_loss_trans': [], 'df_M0D1': []
                    }

        problem_keys = []
        ob_FM_10 = []
        k = 0
        for key, val in ob_FM_key_align_dict.items():
            try:
                A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp = val[0], val[1], val[2], val[3], val[4], val[5], val[6], 0
                alpha = self._calculate_alpha(A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp)
                # print(key, alpha, val[-10])

                if key in list(ob_HOM_key_align_dict.keys()):
                    # update save new
                    save_new['key'].append(key)
                    save_new['A'].append(A_m)
                    save_new['B'].append(B_m)
                    save_new['a'].append(a_m)
                    save_new['b'].append(b_m)
                    save_new['Ri'].append(Ri_m)
                    save_new['L'].append(L_m)
                    save_new['Req'].append(Req_m)
                    save_new['alpha'].append(alpha)
                    save_new['E_stored'].append(val[-10])
                    save_new['Rsh'].append(val[-9])
                    save_new['Q'].append(val[-8])
                    save_new['Epk'].append(val[-7])
                    save_new['Hpk'].append(val[-6])
                    save_new['Eacc'].append(val[-5])
                    save_new['Rsh/Q'].append(val[-4])
                    save_new['Epk/Eacc'].append(val[-3])
                    save_new['Bpk/Eacc'].append(val[-2])
                    save_new['kcc'].append(val[-1])

                    save_new['k_loss_M0'].append(ob_HOM_key_align_dict[key][-4])
                    save_new['k_loss_long'].append(ob_HOM_key_align_dict[key][-3])
                    save_new['k_loss_trans'].append(ob_HOM_key_align_dict[key][-2])
                    save_new['df_M0D1'].append(ob_HOM_key_align_dict[key][-1])

                    self.write_cst_paramters(key, A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m)

            except Exception as e:
                print(f"Key not in both -> {e}")
                problem_keys.append(key)

        print(len(problem_keys), problem_keys)
        print(len(save_new['k_loss_M0']))

        df = pd.DataFrame.from_dict(save_new)
        df.to_excel(f'{save_excel}.xlsx', sheet_name='Sheet1')

    def combine_results_2(self, dir1, dir2, save_excel):

        d_1 = fr.excel_reader(dir1)
        d_2 = fr.excel_reader(dir2)
        d_1 = d_1['Sheet1']
        d_2 = d_2['Sheet1']
        # print(d_2.iloc[0])

        d1_key_align_dict, d2_key_align_dict = {}, {}
        for key, val in d_1.iterrows():
            d1_key_align_dict[int(val['key'])] = list(val)[2:]

        for key, val in d_2.iterrows():
            d2_key_align_dict[int(val['key'])] = list(val)[2:]

        # print(ob_FM_key_align_dict)
        # print()
        # print(ob_HOM_key_align_dict)

        save_new = {'key': [], 'A': [], 'B': [], 'a': [], 'b': [], 'Ri': [], 'L': [], 'Req': [], 'alpha': [],
                    'E_stored': [], 'Rsh': [], 'Q': [], 'Epk': [], 'Hpk': [], 'Eacc': [],
                    'Rsh/Q': [], 'Epk/Eacc': [], 'Bpk/Eacc': [], 'kcc': [],
                    'k_loss_M0': [], 'k_loss_long': [], 'k_loss_trans': [], 'df_M0D1': [],
                    f'Z_long[max(f>{0.5})]': [], f'Z_trans[max(f>{0.6})]': []
                    }

        problem_keys = []
        for key, val in d1_key_align_dict.items():
            try:
                A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp = val[0], val[1], val[2], val[3], val[4], val[5], val[6], 0
                alpha = self._calculate_alpha(A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, L_bp)
                # print(key, alpha, val[-10])

                if key in list(d2_key_align_dict.keys()):
                    # update save new
                    save_new['key'].append(key)
                    save_new['A'].append(A_m)
                    save_new['B'].append(B_m)
                    save_new['a'].append(a_m)
                    save_new['b'].append(b_m)
                    save_new['Ri'].append(Ri_m)
                    save_new['L'].append(L_m)
                    save_new['Req'].append(Req_m)
                    save_new['alpha'].append(alpha)
                    save_new['E_stored'].append(val[-14])
                    save_new['Rsh'].append(val[-13])
                    save_new['Q'].append(val[-12])
                    save_new['Epk'].append(val[-11])
                    save_new['Hpk'].append(val[-10])
                    save_new['Eacc'].append(val[-9])
                    save_new['Rsh/Q'].append(val[-8])
                    save_new['Epk/Eacc'].append(val[-7])
                    save_new['Bpk/Eacc'].append(val[-6])
                    save_new['kcc'].append(val[-5])
                    save_new['k_loss_M0'].append(val[-4])
                    save_new['k_loss_long'].append(val[-3])
                    save_new['k_loss_trans'].append(val[-2])
                    save_new['df_M0D1'].append(val[-1])
                    save_new[f'Z_long[max(f>{0.5})]'].append(d2_key_align_dict[key][-2])
                    save_new[f'Z_trans[max(f>{0.6})]'].append(d2_key_align_dict[key][-1])

                    self.write_cst_paramters(key, A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m)

            except Exception as e:
                print(f"Key not in both -> {e}")
                problem_keys.append(key)

        print(len(problem_keys), problem_keys)
        print(len(save_new['k_loss_M0']))

        df = pd.DataFrame.from_dict(save_new)
        df.to_excel(f'{save_excel}.xlsx', sheet_name='Sheet1')

    def join_excel(self, generic_name, proc_range, save_excel='Combined', request='HOM'):
        if request == 'HOM':
            d_combine = {'key': [], 'A': [], 'B': [], 'a': [], 'b': [], 'Ri': [], 'L': [], 'Req': [],
                         'k_loss_M0': [], 'k_loss_long': [], 'k_loss_trans': [], 'df_M0D1': []}

            for p in range(proc_range[0], proc_range[1] + 1):
                d = fr.excel_reader(
                    fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\modules\data_module\Proc_HOM\{generic_name}_{p}.xlsx')
                d = d['Sheet1']

                for key, val in d.iterrows():
                    d_combine['key'].append(val[1])
                    d_combine['A'].append(val[2])
                    d_combine['B'].append(val[3])
                    d_combine['a'].append(val[4])
                    d_combine['b'].append(val[5])
                    d_combine['Ri'].append(val[6])
                    d_combine['L'].append(val[7])
                    d_combine['Req'].append(val[8])
                    d_combine[f'k_loss_M0'].append(val[9])
                    d_combine[f'k_loss_long'].append(val[10])
                    d_combine[f'k_loss_trans'].append(val[11])
                    d_combine[f'df_M0D1'].append(val[12])
        else:
            d_combine = {'key': [], 'A': [], 'B': [], 'a': [], 'b': [], 'Ri': [], 'L': [], 'Req': [],
                            f'Z_long[max(f>{0.5})]': [], f'Z_trans[max(f>{0.6})]': []}

            for p in range(proc_range[0], proc_range[1]+1):
                d = fr.excel_reader(fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\modules\data_module\Proc_Zmax\{generic_name}_{p}.xlsx')
                d = d['Sheet_1']

                for key, val in d.iterrows():
                    d_combine['key'].append(val[1])
                    d_combine['A'].append(val[2])
                    d_combine['B'].append(val[3])
                    d_combine['a'].append(val[4])
                    d_combine['b'].append(val[5])
                    d_combine['Ri'].append(val[6])
                    d_combine['L'].append(val[7])
                    d_combine['Req'].append(val[8])
                    d_combine[f'Z_long[max(f>{0.5})]'].append(val[9])
                    d_combine[f'Z_trans[max(f>{0.6})]'].append(val[10])

        # print(len(list(d_combine)))
        # print(d_combine)

        df = pd.DataFrame.from_dict(d_combine)
        df.to_excel(f'{save_excel}.xlsx', sheet_name='Sheet1')

    def _calculate_alpha(self, A, B, a, b, Ri, L, Req, L_bp):

        data = ([0 + L_bp, Ri + b, L + L_bp, Req - B],
                [a, b, A, B])  # data = ([h, k, p, q], [a_m, b_m, A_m, B_m])
        x1, y1, x2, y2 = fsolve(self._ellipse_tangent,
                                np.array([a + L_bp, Ri + 0.85 * b, L - A + L_bp, Req - 0.85 * B]),
                                args=data)
        m = (y2 - y1) / (x2 - x1)
        alpha = 180 - np.arctan(m) * 180 / np.pi

        return alpha

    def _ellipse_tangent(self, z, *data):
        coord, dim = data
        h, k, p, q = coord
        a, b, A, B = dim
        x1, y1, x2, y2 = z

        f1 = A**2*b**2*(x1-h)*(y2-q)/(a**2*B**2*(x2-p)*(y1-k)) - 1
        f2 = (x1-h)**2/a**2 + (y1-k)**2/b**2 - 1
        f3 = (x2-p)**2/A**2 + (y2-q)**2/B**2 - 1
        f4 = -b**2*(x1-x2)*(x1-h)/(a**2*(y1-y2)*(y1-k)) - 1

        return f1, f2, f3, f4

    def write_cst_paramters(self, key, A, B, a, b, Ri, L, Req):
        # print("Writing parameters to file")
        cwd = os.getcwd()
        path = os.path.join(cwd, f"CST Shape Parameters_9064\{key}.txt")

        # print(path)
        with open(path, 'w') as f:
            name_list = ['Aeq', 'Beq', 'ai', 'bi', 'Ri', 'L', 'Req', 'x_tr', 'key']

            value_list = [A, B, a, b, Ri, L, Req, 20, key]

            for i in range(len(name_list)):
                f.write(f"{name_list[i]}={value_list[i]}\n")

        # print("Writing to file complete.")


if __name__ == '__main__':
    pr = ProcessData()

#################################################
    # dir = r'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\Cavity Population\fourth_batch_Ri155.json'
    # d = fr.json_reader(dir)
    # # print(d)
    # # wd, pd = pr.weed_maintain_key(d)
    # wd, pd = pr.weed(d)
    # print(wd)
    # print()
    # print(pd)
    # print(len(pd))
    #
    # with open(fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\Cavity Population\fourth_batch_Ri155_weed.json', "w") as outfile:
    #     json.dump(wd, outfile, indent=4, separators=(',', ': '))

#################################################

#################################################
    # dir_FM = fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\modules\data_module\Data_0D_fourth_batch.xlsx'
    # dir_HOM = fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\modules\data_module\HOM_combined_fourth_batch.xlsx'
    # pr.combine_results(dir_FM, dir_HOM, 'combined_fourth_batch')

#################################################

#################################################

    d1 = fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\modules\data_module\COMPLETE_THIRD_BATCH_9276.xlsx'
    d2 = fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\modules\data_module\Zmax_combined_730f770.xlsx'
    pr.combine_results_2(d1, d2, 'COMPLETE_RI150_w_0.73_f_0.77')

#################################################

    # pr.join_excel('Proc', [0, 44], 'Zmax_combined_730f770', request='Zmax')

#################################################

#################################################

    # d = fr.excel_reader(
    #     fr'D:\Dropbox\2D_Codes\ABCI_software\Python_ABCI\modules\data_module\COMPLETE_9064_6D_space.xlsx')
    # d = d['Sheet1']
    #
    # for key, val in d.iterrows():
    #     pr.write_cst_paramters(int(val['key']), val['A'], val['B'], val['a2'], val['b3'], val['Ri'], val['L'], val['Req'])
    #     # print(val)
#################################################
