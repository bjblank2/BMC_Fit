
import numpy as np
import copy
from sklearn.linear_model import LassoCV
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import ElasticNetCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt


def three_way_fit(clusters, energies, counts, comps, fold_pick=10, Normalize=True, Intercept=True, Energy_above_hull=False, names=[]):
    if names == []:
        names = [str(i) for i in range(len(energies))]
    if fold_pick >= 2:
        ###- Lambda expression for scaling to energy above hull -###
        scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
            (y2 - y1) ** 2 + (x2 - x1) ** 2)
        ###- scale to energy above hull -###
        if Energy_above_hull == True: # If you want to FIT to energy above hull (which you don't)
            y1 = min(energies)
            y2 = max(energies)
            x2 = min(comps)
            x1 = max(comps)
            if x2==x1:
                energies = [energies[i]-y1 for i in range(len(energies))]
            else:
                 energies = [scale(comps[i], energies[i], x1, y1, x2, y2) for i in range(len(energies))]

        ###- Set up text for output file -###
        file_out = 'Fit_summery.txt'
        file = open(file_out, 'w')
        file.write('Data set fit summery ' + '\n\n' + 'Clusters:  [[species],[distance],[chem (0) / spin (1)]]' + '\n')
        [file.write(str(clusters[i]) + '\n') for i in range(len(clusters))]
        file.write('\n\nName : Composition : Energy per Atom (eV) : Cluster Count per Atom\n')
        for i in range(len(energies)):
            file.write(names[i] + ' : ' + str(comps[i]) + ' : ' + str(energies[i]) + ' : ' + str(counts[i]) + '\n')
        file.write('\n\n')
        file.write('Without normalization:\n')
        file.write('Name : Composition : Energy per Atom (eV) : Cluster Counts\n')
        for i in range(len(energies)):
            file.write(names[i] + ' : ' + str(comps[i]) + ' : ' + str(energies[i]*sum(comps[i])) + ' : ' + str(list(np.array(counts[i])*sum(comps[i]))) + '\n')
        ###- Set up alphas for CV -###
        alpha_range = [-10, 10]
        alpha_lasso = np.logspace(alpha_range[0], alpha_range[1], num=1000) # for lasso cv
        #n_alphas = 1010
        #alpha_ridge = np.logspace(-15, 10, n_alphas) # for ridge cv
        alpha_ridge = alpha_lasso
        ###- Set range for plot -###
        axis_range = [min(energies) * 1.0001, max(energies) * .9999]
        kf = KFold(n_splits=fold_pick, shuffle=True)
        # LASSO and RIDGE, Cross-Validation, Lin Reg without CV
        lassocv = LassoCV(alphas=alpha_lasso, normalize=Normalize, fit_intercept=Intercept, cv=kf, max_iter=1e9)
        ridgecv = RidgeCV(alphas=alpha_ridge, normalize=Normalize, fit_intercept=Intercept, cv=None, store_cv_values=True)
        linreg = LinearRegression(fit_intercept=Intercept, normalize=Normalize)
        # Fit to data for each method
        lassocv.fit(counts, energies) # do fit for lasso
        ridgecv.fit(counts, energies) # do fit for ridge
        linreg.fit(counts, energies) # do fit for linreg
        lassocv_rmse = np.sqrt(lassocv.mse_path_)
        ridgecv_rmse = np.sqrt(ridgecv.cv_values_)
        # Set up Random Forrest regression, max depth is hard coded to 5 but this can be played with
        #RandF_reg = RandomForestRegressor(max_depth=5, random_state=0)
        #RandF_reg.fit(counts, energies) # for random forrest fit

        ### Get results ready for energy above hull plots ###
        y1 = min(energies)
        y2 = max(energies)
        x2 = min([comps[i][1]/np.sum(comps[i]) for i in range(len(comps))])
        x1 = max([comps[i][1]/np.sum(comps[i]) for i in range(len(comps))])
        scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
            (y2 - y1) ** 2 + (x2 - x1) ** 2)
        eahDFT = [scale(comps[i][1]/np.sum(comps[i]), energies[i], x1, y1, x2, y2) for i in range(len(energies))]
        axis_rangeEAH = [-0.002, max(eahDFT) * 1.1]


        ########################################################################################################################
        ################ RANDOM FOREST FIT #####################################################################################
        ########################################################################################################################
        # file.write("\n\n#### Random Forest #### ")
        # # Plot Fit vs DFT
        #
        # cluster_energy_RF = RandF_reg.predict(counts)
        # #print(RandF_reg.estimators_) # Comment in if you want to see the estimator generated by random forrest (its a bit messy)
        # #print(RandF_reg.get_params()) # ''
        # plt.figure()
        # plt.scatter(energies, cluster_energy_RF, color='b', alpha=0.5)
        # plt.plot(axis_range, axis_range, 'k', alpha=0.5)
        # plt.xlim(axis_range)
        # plt.ylim(axis_range)
        # plt.gca().set_aspect('equal')
        # plt.xlabel('Energy, DFT')
        # plt.ylabel('Energy, CE')
        # plt.title('Random Forest Fit Comparison: ' + name)
        # plt.tight_layout()
        # plt.show()
        # eahCE = [scale(comps[i], cluster_energy_RF[i], x1, y1, x2, y2) for i in range(len(cluster_energy_RF))]
        # plt.scatter(eahDFT, eahCE, color='b', alpha=0.5)
        # plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
        # plt.xlim(axis_rangeEAH)
        # plt.ylim(axis_rangeEAH)
        # plt.gca().set_aspect('equal')
        # plt.xlabel('EAH, DFT')
        # plt.ylabel('EAH, CE')
        # plt.title('Random Forest Fit Comparison: ' + name)
        # plt.tight_layout()
        # plt.show()



        ########################################################################################################################
        ############### Elastic Net ############################################################################################
        ########################################################################################################################

        # file.write("\n\n### ELN ### \nk-folds cross validation\n")
        # file.write("alpha: %7.6f\n" % elcv.alpha_)
        # #file.write("avg rmse: %7.4f\n" % min(ridgecv_rmse.mean(axis=-1)))
        # file.write("score: %7.4f\n" % elcv.score(counts, energies))
        # file.write("non-zero coefficient: %7.4f\n" % np.count_nonzero(elcv.coef_))
        #
        # cluster_energy_ce = elcv.predict(counts)
        # #return_ernrgys = elcv.copy()
        # plt.figure()
        # plt.scatter(energies, cluster_energy_ce, color='tab:orange', alpha=0.5)
        # plt.plot(axis_range, axis_range, 'k', alpha=0.5)
        # plt.xlim(axis_range)
        # plt.ylim(axis_range)
        # plt.gca().set_aspect('equal')
        # plt.xlabel('Energy, DFT')
        # plt.ylabel('Energy, CE')
        # plt.title('ELN Fit Comparison: ' + name)
        # plt.tight_layout()
        # plt.show()
        # eahCE = [scale(comps[i], cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
        # plt.scatter(eahDFT, eahCE, color='tab:orange', alpha=0.5)
        # plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
        # plt.xlim(axis_rangeEAH)
        # plt.ylim(axis_rangeEAH)
        # plt.gca().set_aspect('equal')
        # plt.xlabel('EAH, DFT')
        # plt.ylabel('EAH, CE')
        # plt.title('LASSO Fit Comparison: ' + name)
        # plt.tight_layout()
        # plt.show()
        #
        # # Show Non-zero clusters
        # cluster_energy_new = []
        # for i in range(len(energies)):
        #     cluster_energy_new.append(energies[i] - cluster_energy_ce[i])
        # cluster_coef = []
        # cluster_pick = []
        # cluster_coef.append(elcv.intercept_)
        # cluster_coef_all = elcv.coef_
        # cluster_nonzero = [c for c, v in enumerate(cluster_coef_all) if abs(v) >= 0.00000000001 ]
        # for i in cluster_nonzero:
        #     cluster_coef.append(cluster_coef_all[i])
        #     cluster_pick.append(clusters[i])
        # file.write("\n Clusters \n")
        # for i in range(len(cluster_pick)):
        #     if len(cluster_pick[i]) == 2:
        #         file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
        #             cluster_coef[i + 1]) + '\n')
        #     else:
        #         file.write(
        #             str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(cluster_pick[i][2][0]) + ':' + str(
        #                 cluster_coef[i + 1]) + '\n')
        # file.write("\n")
        # file.write("\n")




        ########################################################################################################################
        ################ LASSO FIT #############################################################################################
        ########################################################################################################################
        cluster_energy_ce = lassocv.predict(counts)
        rmse = np.sqrt(mean_squared_error(energies, cluster_energy_ce))
        file.write("\n\n#### LASSO #### \nk-folds cross validation\n")
        file.write("rmse of fit:%7.6f\n" % rmse)
        file.write("alpha: %7.6f\n" % lassocv.alpha_)
        file.write("avg rmse: %7.4f\n" % min(lassocv_rmse.mean(axis=-1)))
        file.write("score: %7.4f\n" % lassocv.score(counts, energies))
        file.write("non-zero coefficient: %7.4f\n" % np.count_nonzero(lassocv.coef_))
        file.write('Intercept: ')
        file.write(str(lassocv.intercept_))
        file.write('\n')
        # Show data from cross validation / cluster picking
        plt.figure()
        m_log_alphas = -np.log10(lassocv.alphas_)
        plt.plot(m_log_alphas, lassocv_rmse, ':')
        plt.plot(m_log_alphas, lassocv_rmse.mean(axis=-1), 'k', label='Average across the folds', linewidth=2)
        plt.axvline(-np.log10(lassocv.alpha_), linestyle='--', color='k', label='alpha: CV estimate')
        plt.xlabel('-log(alpha)')
        plt.ylabel('Root-mean-square error')
        plt.title('Root-mean-square error on each fold')
        plt.legend()
        plt.tight_layout()
        plt.show()
        # Plot Fit vs DFT
        plt.figure()
        plt.scatter(energies, cluster_energy_ce, color='b', alpha=0.5)
        plt.plot(axis_range, axis_range, 'k', alpha=0.5)
        plt.xlim(axis_range)
        plt.ylim(axis_range)
        plt.gca().set_aspect('equal')
        plt.xlabel('Energy, DFT')
        plt.ylabel('Energy, CE')
        plt.title('LASSO Fit Comparison')
        plt.tight_layout()
        plt.show()
        eahCE = [scale(comps[i][1]/np.sum(comps[i]), cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
        plt.scatter(eahDFT, eahCE, color='b', alpha=0.5)
        plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
        plt.xlim(axis_rangeEAH)
        plt.ylim(axis_rangeEAH)
        plt.gca().set_aspect('equal')
        plt.xlabel('EAH, DFT')
        plt.ylabel('EAH, CE')
        plt.title('LASSO Fit Comparison')
        plt.tight_layout()
        plt.show()

        # Show Non-zero clusters
        cluster_energy_new = []
        for i in range(len(energies)):
            cluster_energy_new.append(energies[i] - cluster_energy_ce[i])
        cluster_coef = []
        cluster_pick = []
        cluster_coef.append(lassocv.intercept_)
        cluster_coef_all = lassocv.coef_
        cluster_nonzero = [c for c, v in enumerate(cluster_coef_all)] # if abs(v) >= 0.00000000001 ] #only if you dont want zeros
        for i in cluster_nonzero:
            cluster_coef.append(cluster_coef_all[i])
            cluster_pick.append(clusters[i])
        file.write("\n Clusters \n")
        for i in range(len(cluster_pick)):
            if len(cluster_pick[i]) == 2:
                file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
                    cluster_coef[i + 1]) + '\n')
            else:
                file.write(
                    str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(cluster_pick[i][2][0]) + ':' + str(
                        cluster_coef[i + 1]) + '\n')
        file.write("\n")
        file.write("\n")

        ########################################################################################################################
        ############# RIDGE FIT ################################################################################################
        ########################################################################################################################
        cluster_energy_ce = ridgecv.predict(counts)
        rmse = np.sqrt(mean_squared_error(energies, cluster_energy_ce))
        file.write("### RIDGE ### \nk-folds cross validation\n")
        file.write("rmse of fit: %7.6f\n" % rmse)
        file.write("alpha: %7.6f\n" % ridgecv.alpha_)
        file.write("avg rmse: %7.4f\n" % min(ridgecv_rmse.mean(axis=-1)))
        file.write("score: %7.4f\n" % ridgecv.score(counts, energies))
        file.write("non-zero coefficient: %7.4f\n" % np.count_nonzero(ridgecv.coef_))

        # plt.figure()
        cv_vs_alpha = -np.log10(ridgecv.cv_values_)
        alphas = np.array(alpha_ridge)
        # plt.plot(m_log_alphas, ridgecv_rmse, ':')
        # plt.plot(m_log_alphas, ridgecv_rmse.mean(axis=-1), 'k', label='Average across the folds', linewidth=2)
        # plt.axvline(-np.log10(ridgecv.alpha_), linestyle='--', color='k', label='alpha: CV estimate')
        #for cvs in cv_vs_alpha:
        #    plt.plot(alphas, cvs, ':')
        #plt.plot(alphas, cv_vs_alpha.mean(axis=1), 'k', label='Average across the folds', linewidth=2)
        #plt.axvline(ridgecv.alpha_, linestyle='--', color='k', label='alpha: CV estimate')

        #plt.xlabel('-log(alpha)')
        #plt.ylabel('Root-mean-square error')
        #plt.title('Root-mean-square error on each fold: ' + name)
        #plt.legend()
        #plt.tight_layout()
        #plt.show()

        # Plot Fit vs DFT
        plt.figure()
        plt.scatter(energies, cluster_energy_ce, color="r", alpha=0.5)
        plt.plot(axis_range, axis_range, 'k', alpha=0.5)
        plt.xlim(axis_range)
        plt.ylim(axis_range)
        plt.gca().set_aspect('equal')
        plt.xlabel('Energy, DFT')
        plt.ylabel('Energy, CE')
        plt.title('RIDGE Fit Comparison')
        plt.tight_layout()
        plt.show()
        eahCE = [scale(comps[i][1]/np.sum(comps[i]), cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
        plt.scatter(eahDFT, eahCE, color='r', alpha=0.5)
        plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
        plt.xlim(axis_rangeEAH)
        plt.ylim(axis_rangeEAH)
        plt.gca().set_aspect('equal')
        plt.xlabel('EAH, DFT')
        plt.ylabel('EAH, CE')
        plt.title('RIDGE Fit Comparison')
        plt.tight_layout()
        plt.show()
        # Show Non-zero clusters
        cluster_coef = []
        cluster_pick = []
        cluster_coef.append(ridgecv.intercept_)
        cluster_coef_all = ridgecv.coef_
        cluster_nonzero = [c for c, v in enumerate(cluster_coef_all) ] #if abs(v) >= 0.00000000001] # only if you dont want zeros
        for i in cluster_nonzero:
            cluster_coef.append(cluster_coef_all[i])
            cluster_pick.append(clusters[i])
        file.write("\n Clusters\n")
        for i in range(len(cluster_pick)):
            if len(cluster_pick[i]) == 2:
                file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
                    cluster_coef[i + 1]) + '\n')
            else:
                file.write(
                    str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(cluster_pick[i][2][0]) + ':' + str(
                        cluster_coef[i + 1]) + '\n')

        ########################################################################################################################
        ############# LIN REG FIT ##############################################################################################
        ########################################################################################################################
        cluster_energy_ce = linreg.predict(counts)
        rmse = np.sqrt(mean_squared_error(energies, cluster_energy_ce))
        file.write("\n #### Lin Reg #### \nNo cross validation\n")
        file.write("rmse of fit %7.4f\n" % rmse)
        file.write('Intercept: %7.4f\n' % linreg.intercept_)
        # Plot Fit vs DFT
        plt.figure()
        plt.scatter(energies, cluster_energy_ce, color="g", alpha=0.5)
        plt.plot(axis_range, axis_range, 'k', alpha=0.5)
        plt.xlim(axis_range)
        plt.ylim(axis_range)
        plt.gca().set_aspect('equal')
        plt.xlabel('Energy, DFT')
        plt.ylabel('Energy, CE')
        plt.title('LinReg Fit Comparison')
        plt.tight_layout()
        plt.show()
        eahCE = [scale(comps[i][1]/np.sum(comps[i]), cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
        plt.scatter(eahDFT, eahCE, color='g', alpha=0.5)
        plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
        plt.xlim(axis_rangeEAH)
        plt.ylim(axis_rangeEAH)
        plt.gca().set_aspect('equal')
        plt.xlabel('EAH, DFT')
        plt.ylabel('EAH, CE')
        plt.title('LinReg Fit Comparison')
        plt.tight_layout()
        plt.show()
        # Show Non-zero clusters
        cluster_coef = []
        cluster_pick = []
        cluster_coef.append(linreg.intercept_)
        cluster_coef_all = linreg.coef_
        cluster_nonzero = [c for c, v in enumerate(cluster_coef_all)] # if abs(v) >= 0.00000000001] # only if you dont want zeros
        for i in cluster_nonzero:
            cluster_coef.append(cluster_coef_all[i])
            cluster_pick.append(clusters[i])
        file.write('\nClusters\n')
        for i in range(len(cluster_pick)):
            if len(cluster_pick[i]) == 2:
                file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
                    cluster_coef[i + 1]) + '\n')
            else:
                file.write(
                    str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(cluster_pick[i][2][0]) + ':' + str(
                        cluster_coef[i + 1]) + '\n')
        file.write('\n')
        file.close()

        return lassocv

    else:

        ###- Lambda expression for scaling to energy above hull -###
        scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
            (y2 - y1) ** 2 + (x2 - x1) ** 2)
        ###- scale to energy above hull -###
        if Energy_above_hull == True:  # If you want to FIT to energy above hull (which you don't)
            y1 = min(energies)
            y2 = max(energies)
            x2 = min([comps[i][1]/np.sum(comps[i]) for i in range(len(comps))])
            x1 = max([comps[i][1]/np.sum(comps[i]) for i in range(len(comps))])
            if x2 == x1:
                energies = [energies[i] - y1 for i in range(len(energies))]
            else:
                energies = [scale(comps[i], energies[i], x1, y1, x2, y2) for i in range(len(energies))]

        ###- Set up text for output file -###
        file_out = 'Fit_summery.txt'
        file = open(file_out, 'w')
        file.write('Data set fit summery' + '\n\n' + 'Clusters:  [[species],[distance],[chem (0) / spin (1)]]' + '\n')
        [file.write(str(clusters[i]) + '\n') for i in range(len(clusters))]
        file.write('\n\nEnergy per Atom (eV) : Cluster Count per Atom\n')
        for i in range(len(energies)):
            file.write(str(energies[i]) + ' : ' + str(counts[i]) + '\n')


        axis_range = [min(energies) * 1.0001, max(energies) * .9999]

        linreg = LinearRegression(fit_intercept=Intercept, normalize=Normalize)
        linreg.fit(counts, energies)  # do fit for linreg
        ### Get results ready for energy above hull plots ###
        y1 = min(energies)
        y2 = max(energies)
        x2 = min([comps[i][1]/np.sum(comps[i]) for i in range(len(comps))])
        x1 = max([comps[i][1]/np.sum(comps[i]) for i in range(len(comps))])
        scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
            (y2 - y1) ** 2 + (x2 - x1) ** 2)
        eahDFT = [scale(comps[i][1], energies[i], x1, y1, x2, y2) for i in range(len(energies))]
        axis_rangeEAH = [-0.002, max(eahDFT) * 1.1]

        # Plot Fit vs DFT
        cluster_energy_ce = linreg.predict(counts)
        plt.figure()
        plt.scatter(energies, cluster_energy_ce, color="g", alpha=0.5)
        plt.plot(axis_range, axis_range, 'k', alpha=0.5)
        plt.xlim(axis_range)
        plt.ylim(axis_range)
        plt.gca().set_aspect('equal')
        plt.xlabel('Energy, DFT')
        plt.ylabel('Energy, CE')
        plt.title('LinReg Fit Comparison')
        plt.tight_layout()
        plt.show()
        eahCE = [scale(comps[i][1], cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
        plt.scatter(eahDFT, eahCE, color='g', alpha=0.5)
        plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
        plt.xlim(axis_rangeEAH)
        plt.ylim(axis_rangeEAH)
        plt.gca().set_aspect('equal')
        plt.xlabel('EAH, DFT')
        plt.ylabel('EAH, CE')
        plt.title('LinReg Fit Comparison')
        plt.tight_layout()
        plt.show()
        # Show Non-zero clusters
        cluster_coef = []
        cluster_pick = []
        cluster_coef.append(linreg.intercept_)
        cluster_coef_all = linreg.coef_
        #cluster_nonzero = [c for c, v in enumerate(cluster_coef_all) if abs(v) >= 0.00000000001] # comment this in if you want to display only nonzero coefs
        cluster_nonzero = [c for c, v in enumerate(cluster_coef_all)]
        for i in cluster_nonzero:
            cluster_coef.append(cluster_coef_all[i])
            cluster_pick.append(clusters[i])
        file.write('\nClusters\n')
        for i in range(len(cluster_pick)):
            if len(cluster_pick[i]) == 2:
                file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
                    cluster_coef[i + 1]) + '\n')
            else:
                file.write(
                    str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(
                        cluster_pick[i][2][0]) + ':' + str(
                        cluster_coef[i + 1]) + '\n')
        file.write('\n')
        file.close()

def two_way_fit_comp(clusters, energies, counts, comps, fold_pick=10, Normalize=True, Intercept=True, Energy_above_hull = True, name=''):
    ###- Lambda expression for scaling to energy above hull -###
    scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
        (y2 - y1) ** 2 + (x2 - x1) ** 2)
    ###- scale to energy above hull -###
    if Energy_above_hull == True: # If you want to FIT to energy above hull (which you don't)
        y1 = min(energies)
        y2 = max(energies)
        x2 = min(comps)
        x1 = max(comps)
        if x2==x1:
            energies = [energies[i]-y1 for i in range(len(energies))]
        else:
             energies = [scale(comps[i], energies[i], x1, y1, x2, y2) for i in range(len(energies))]

    ###- Set up text for output file -###
    # file_out = 'Fit_summery.txt'
    # file = open(file_out, 'w')
    # file.write('Data set: ' + name + '\n\n' + 'Clusters:  [[species],[distance],[chem (0) / spin (1)]]' + '\n')
    # [file.write(str(clusters[i]) + '\n') for i in range(len(clusters))]
    # file.write('\n\nEnergy per Atom (eV) : Cluster Count per Atom\n')
    # for i in range(len(energies)):
    #     file.write(str(energies[i]) + ' : ' + str(counts[i]) + '\n')

    ###- Set up alphas for CV -###
    alpha_range = [0.0000000001, 4]
    alphas = np.linspace(alpha_range[0], alpha_range[1], num=1000) # for lasso cv
    ###- Set range for plot -###
    axis_range = [min(energies) * 1.0001, max(energies) * .9999]
    lassoR2s = []
    ridgeR2s = []
    for alpha in alphas:
        lasso = Lasso(alpha=alpha, normalize=Normalize, fit_intercept=Intercept)
        ridge = Ridge(alpha=alpha, normalize=Normalize, fit_intercept=Intercept)
        # Fit to data for each method
        lasso.fit(counts, energies) # do fit for lasso
        ridge.fit(counts, energies) # do fit for ridge
        lassoR2s.append(lasso.score(counts, energies))
        ridgeR2s.append(ridge.score(counts, energies))
    plt.plot(alphas, lassoR2s, 'b')
    plt.plot(alphas, ridgeR2s, 'r')
    plt.show()

def forced_param_fit(forced_clusters, clusters, energies, counts, comps, fold_pick=10, Normalize=True, Intercept=True, Energy_above_hull = True, name=''):
    ###- Lambda expression for scaling to energy above hull -###
    scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
        (y2 - y1) ** 2 + (x2 - x1) ** 2)
    ###- scale to energy above hull -###
    if Energy_above_hull == True:  # If you want to FIT to energy above hull (which you don't)
        y1 = min(energies)
        y2 = max(energies)
        x2 = min(comps)
        x1 = max(comps)
        if x2 == x1:
            energies = [energies[i] - y1 for i in range(len(energies))]
        else:
            energies = [scale(comps[i], energies[i], x1, y1, x2, y2) for i in range(len(energies))]

    ###- Set up text for output file -###
    file_out = 'Fit_summery.txt'
    file = open(file_out, 'w')
    file.write('Data set: ' + name + '\n\n' + 'Clusters:  [[species],[distance],[chem (0) / spin (1)]]' + '\n')
    [file.write(str(clusters[i]) + '\n') for i in range(len(clusters))]
    file.write('\n\nEnergy per Atom (eV) : Cluster Count per Atom\n')
    for i in range(len(energies)):
        file.write(str(energies[i]) + ' : ' + str(counts[i]) + '\n')

    ###- Set up alphas for CV -###
    alpha_range = [-10, 10]
    alpha_lasso = np.logspace(alpha_range[0], alpha_range[1], num=1000)  # for lasso cv
    alpha_ridge = alpha_lasso
    ###- Set range for plot -###
    kf = KFold(n_splits=fold_pick, shuffle=True)
    # LASSO and RIDGE, Cross-Validation, Lin Reg without CV
    lassocv1 = LassoCV(alphas=alpha_lasso, normalize=Normalize, fit_intercept=True, cv=kf, max_iter=1e9)
    lassocv2 = LassoCV(alphas=alpha_lasso, normalize=Normalize, fit_intercept=False, cv=kf, max_iter=1e9)
    ridgecv1 = RidgeCV(alphas=alpha_ridge, normalize=Normalize, fit_intercept=True, cv=None, store_cv_values=True)
    ridgecv2 = RidgeCV(alphas=alpha_ridge, normalize=Normalize, fit_intercept=False, cv=None, store_cv_values=True)

    #linreg = LinearRegression(fit_intercept=Intercept, normalize=Normalize)
    # Fit to data for each method
    lassocv1.fit(counts, energies)  # do fit for lasso
    lassocv2.fit(counts, energies)  # do fit for lasso
    ridgecv1.fit(counts, energies)
    ridgecv2.fit(counts, energies)
    #linreg.fit(counts, energies)  # do fit for linreg
    lassocv_rmse = np.sqrt(lassocv1.mse_path_)
    ridgecv_rmse = np.sqrt(ridgecv1.cv_values_)
    counts2 = copy.deepcopy(counts)
    clusters2 = copy.deepcopy(clusters)
    ####################################################################################################################
    for i in range(len(energies)):
        for j in range(len(clusters)):
            for k in range(len(forced_clusters)):
                if j == forced_clusters[k][0]:
                    #counts2[i].pop(j)
                    counts2[i][j] = 0
    for i in range(len(ridgecv2.coef_)):
        for j in range(len(forced_clusters)):
            if i == forced_clusters[j][0]:
                ridgecv2.coef_[i] = forced_clusters[j][1]
            else:
                ridgecv2.coef_[i] = 0.0
    ####################################################################################################################
    ridge_energy_1 = ridgecv2.predict(counts)
    ridge_energy = np.subtract(energies, ridge_energy_1)
    ridgecv1.fit(counts2, ridge_energy)
    lassocv1.fit(counts2, ridge_energy)
    #coefs_test = copy.deepcopy(ridgecv1.coef_)
    # ridgecv1.fit(counts2, energies)
    # for i in range(len(ridgecv1.coef_)):
    #     ridgecv1.coef_[i] += coefs_test[i]
    ### Get results ready for energy above hull plots ###
    y1 = min(ridge_energy)
    y2 = max(ridge_energy)
    x2 = min(comps)
    x1 = max(comps)
    scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
        (y2 - y1) ** 2 + (x2 - x1) ** 2)
    eahDFT = [scale(comps[i], ridge_energy[i], x1, y1, x2, y2) for i in range(len(ridge_energy))]
    axis_rangeEAH = [-0.002, max(eahDFT) * 1.1]


    ########################################################################################################################
    ############# RIDGE FIT ################################################################################################
    ########################################################################################################################
    axis_range = [min(ridge_energy) * 1.0001, max(ridge_energy) * .9999]
    file.write("### RIDGE ### \nk-folds cross validation\n")
    file.write("alpha: %7.6f\n" % ridgecv1.alpha_)
    file.write("avg rmse: %7.4f\n" % min(ridgecv_rmse.mean(axis=-1)))
    file.write("score: %7.4f\n" % ridgecv1.score(counts2, ridge_energy))
    file.write("non-zero coefficient: %7.4f\n" % np.count_nonzero(ridgecv1.coef_))

    plt.figure()
    cv_vs_alpha = -np.log10(ridgecv1.cv_values_)
    alphas = np.array(alpha_ridge)
    # plt.plot(m_log_alphas, ridgecv_rmse, ':')
    # plt.plot(m_log_alphas, ridgecv_rmse.mean(axis=-1), 'k', label='Average across the folds', linewidth=2)
    # plt.axvline(-np.log10(ridgecv.alpha_), linestyle='--', color='k', label='alpha: CV estimate')
    # for cvs in cv_vs_alpha:
    #    plt.plot(alphas, cvs, ':')
    # plt.plot(alphas, cv_vs_alpha.mean(axis=1), 'k', label='Average across the folds', linewidth=2)
    # plt.axvline(ridgecv.alpha_, linestyle='--', color='k', label='alpha: CV estimate')

    # plt.xlabel('-log(alpha)')
    # plt.ylabel('Root-mean-square error')
    # plt.title('Root-mean-square error on each fold: ' + name)
    # plt.legend()
    # plt.tight_layout()
    # plt.show()

    # Plot Fit vs DFT
    cluster_energy_ce = ridgecv1.predict(counts2)
    plt.figure()
    plt.scatter(ridge_energy, cluster_energy_ce, color="r", alpha=0.5)
    plt.plot(axis_range, axis_range, 'k', alpha=0.5)
    #plt.xlim(axis_range)
    #plt.ylim(axis_range)
    plt.gca().set_aspect('equal')
    plt.xlabel('Energy, DFT')
    plt.ylabel('Energy, CE')
    plt.title('RIDGE Fit Comparison: ' + name)
    #plt.tight_layout()
    plt.show()
    eahCE = [scale(comps[i], cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
    plt.scatter(eahDFT, eahCE, color='r', alpha=0.5)
    plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
    #plt.xlim(axis_rangeEAH)
    #plt.ylim(axis_rangeEAH)
    plt.gca().set_aspect('equal')
    plt.xlabel('EAH, DFT')
    plt.ylabel('EAH, CE')
    plt.title('RIDGE Fit Comparison: ' + name)
    #plt.tight_layout()
    plt.show()
    # Show Non-zero clusters
    cluster_coef = []
    cluster_pick = []
    cluster_coef.append(ridgecv1.intercept_)
    cluster_coef_all = ridgecv1.coef_
    cluster_nonzero = [c for c, v in enumerate(cluster_coef_all) if abs(v) >= 0.00000000001]
    for i in cluster_nonzero:
        cluster_coef.append(cluster_coef_all[i])
        cluster_pick.append(clusters[i])
    file.write("\n Clusters\n")
    for i in range(len(cluster_pick)):
        if len(cluster_pick[i]) == 2:
            file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
                cluster_coef[i + 1]) + '\n')
        else:
            file.write(
                str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(cluster_pick[i][2][0]) + ':' + str(
                    cluster_coef[i + 1]) + '\n')


    ########################################################################################################################
    ############# LASSO FIT ################################################################################################
    ########################################################################################################################
    axis_range = [min(ridge_energy) * 1.0001, max(ridge_energy) * .9999]
    file.write("### RIDGE ### \nk-folds cross validation\n")
    file.write("alpha: %7.6f\n" % lassocv1.alpha_)
    file.write("avg rmse: %7.4f\n" % min(lassocv_rmse.mean(axis=-1)))
    file.write("score: %7.4f\n" % lassocv1.score(counts2, ridge_energy))
    file.write("non-zero coefficient: %7.4f\n" % np.count_nonzero(lassocv1.coef_))

    plt.figure()
    cv_vs_alpha = -np.log10(lassocv1.cv_values_)
    alphas = np.array(alpha_ridge)
    # plt.plot(m_log_alphas, ridgecv_rmse, ':')
    # plt.plot(m_log_alphas, ridgecv_rmse.mean(axis=-1), 'k', label='Average across the folds', linewidth=2)
    # plt.axvline(-np.log10(ridgecv.alpha_), linestyle='--', color='k', label='alpha: CV estimate')
    # for cvs in cv_vs_alpha:
    #    plt.plot(alphas, cvs, ':')
    # plt.plot(alphas, cv_vs_alpha.mean(axis=1), 'k', label='Average across the folds', linewidth=2)
    # plt.axvline(ridgecv.alpha_, linestyle='--', color='k', label='alpha: CV estimate')

    # plt.xlabel('-log(alpha)')
    # plt.ylabel('Root-mean-square error')
    # plt.title('Root-mean-square error on each fold: ' + name)
    # plt.legend()
    # plt.tight_layout()
    # plt.show()

    # Plot Fit vs DFT
    cluster_energy_ce = lassocv1.predict(counts2)
    plt.figure()
    plt.scatter(ridge_energy, cluster_energy_ce, color="r", alpha=0.5)
    plt.plot(axis_range, axis_range, 'k', alpha=0.5)
    #plt.xlim(axis_range)
    #plt.ylim(axis_range)
    plt.gca().set_aspect('equal')
    plt.xlabel('Energy, DFT')
    plt.ylabel('Energy, CE')
    plt.title('RIDGE Fit Comparison: ' + name)
    #plt.tight_layout()
    plt.show()
    eahCE = [scale(comps[i], cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
    plt.scatter(eahDFT, eahCE, color='r', alpha=0.5)
    plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
    #plt.xlim(axis_rangeEAH)
    #plt.ylim(axis_rangeEAH)
    plt.gca().set_aspect('equal')
    plt.xlabel('EAH, DFT')
    plt.ylabel('EAH, CE')
    plt.title('RIDGE Fit Comparison: ' + name)
    #plt.tight_layout()
    plt.show()
    # Show Non-zero clusters
    cluster_coef = []
    cluster_pick = []
    cluster_coef.append(lassocv1.intercept_)
    cluster_coef_all = lassocv1.coef_
    cluster_nonzero = [c for c, v in enumerate(cluster_coef_all) if abs(v) >= 0.00000000001]
    for i in cluster_nonzero:
        cluster_coef.append(cluster_coef_all[i])
        cluster_pick.append(clusters[i])
    file.write("\n Clusters\n")
    for i in range(len(cluster_pick)):
        if len(cluster_pick[i]) == 2:
            file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
                cluster_coef[i + 1]) + '\n')
        else:
            file.write(
                str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(cluster_pick[i][2][0]) + ':' + str(
                    cluster_coef[i + 1]) + '\n')

def forced_param_ridge_fit(forced_clusters, clusters, energies, counts, comps, fold_pick=10, Normalize=True, Intercept=True, Energy_above_hull = True, name=''):
    ###- Lambda expression for scaling to energy above hull -###
    scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
        (y2 - y1) ** 2 + (x2 - x1) ** 2)
    ###- scale to energy above hull -###
    if Energy_above_hull == True:  # If you want to FIT to energy above hull (which you don't)
        y1 = min(energies)
        y2 = max(energies)
        x2 = min(comps)
        x1 = max(comps)
        if x2 == x1:
            energies = [energies[i] - y1 for i in range(len(energies))]
        else:
            energies = [scale(comps[i], energies[i], x1, y1, x2, y2) for i in range(len(energies))]

    ###- Set up text for output file -###
    file_out = 'Fit_summery.txt'
    file = open(file_out, 'w')
    file.write('Data set: ' + name + '\n\n' + 'Clusters:  [[species],[distance],[chem (0) / spin (1)]]' + '\n')
    [file.write(str(clusters[i]) + '\n') for i in range(len(clusters))]
    file.write('\n\nEnergy per Atom (eV) : Cluster Count per Atom\n')
    for i in range(len(energies)):
        file.write(str(energies[i]) + ' : ' + str(counts[i]) + '\n')

    ###- Set up alphas for CV -###
    alpha_range = [-10, 10]
    alpha_ridge = np.logspace(alpha_range[0], alpha_range[1], num=1000)  # for lasso cv
    ###- Set range for plot -###
    kf = KFold(n_splits=fold_pick, shuffle=True)
    # LASSO and RIDGE, Cross-Validation, Lin Reg without CV
    ridgecv1 = RidgeCV(alphas=alpha_ridge, normalize=Normalize, fit_intercept=True, cv=None, store_cv_values=True)
    ridgecv2 = RidgeCV(alphas=alpha_ridge, normalize=Normalize, fit_intercept=False, cv=None, store_cv_values=True)

    #linreg = LinearRegression(fit_intercept=Intercept, normalize=Normalize)
    # Fit to data for each method
    ridgecv1.fit(counts, energies)
    ridgecv2.fit(counts, energies)
    #linreg.fit(counts, energies)  # do fit for linreg
    ridgecv_rmse = np.sqrt(ridgecv1.cv_values_)
    counts2 = copy.deepcopy(counts)
    clusters2 = copy.deepcopy(clusters)
    ####################################################################################################################
    for i in range(len(energies)):
        for j in range(len(clusters)):
            for k in range(len(forced_clusters)):
                if j == forced_clusters[k][0]:
                    #counts2[i].pop(j)
                    counts2[i][j] = 0
    for i in range(len(ridgecv2.coef_)):
        for j in range(len(forced_clusters)):
            if i == forced_clusters[j][0]:
                ridgecv2.coef_[i] = forced_clusters[j][1]
            else:
                ridgecv2.coef_[i] = 0.0
    ####################################################################################################################
    ridge_energy_1 = ridgecv2.predict(counts)
    ridge_energy = np.subtract(energies, ridge_energy_1)
    ridgecv1.fit(counts2, ridge_energy)
    #coefs_test = copy.deepcopy(ridgecv1.coef_)
    # ridgecv1.fit(counts2, energies)
    # for i in range(len(ridgecv1.coef_)):
    #     ridgecv1.coef_[i] += coefs_test[i]
    ### Get results ready for energy above hull plots ###
    y1 = min(ridge_energy)
    y2 = max(ridge_energy)
    x2 = min(comps)
    x1 = max(comps)
    scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
        (y2 - y1) ** 2 + (x2 - x1) ** 2)
    eahDFT = [scale(comps[i], ridge_energy[i], x1, y1, x2, y2) for i in range(len(ridge_energy))]
    axis_rangeEAH = [-0.002, max(eahDFT) * 1.1]


    ########################################################################################################################
    ############# RIDGE FIT ################################################################################################
    ########################################################################################################################
    axis_range = [min(ridge_energy) * 1.0001, max(ridge_energy) * .9999]
    for i in range(len(ridgecv1.coef_)):
        for j in range(len(forced_clusters)):
            if i == forced_clusters[j][0]:
                ridgecv1.coef_[i] = forced_clusters[j][1]
    cluster_energy_ce = ridgecv1.predict(counts)
    rmse = np.sqrt(mean_squared_error(energies, cluster_energy_ce))
    file.write("### RIDGE ### \nk-folds cross validation\n")
    file.write("forced clusters: " + str(forced_clusters) + "\n")
    file.write("rmse of fit: %7.6f\n" % rmse)
    file.write("alpha: %7.6f\n" % ridgecv1.alpha_)
    file.write("avg rmse: %7.4f\n" % min(ridgecv_rmse.mean(axis=-1)))
    file.write("score: %7.4f\n" % ridgecv1.score(counts2, ridge_energy))
    file.write("non-zero coefficient: %7.4f\n" % np.count_nonzero(ridgecv1.coef_))

    plt.figure()
    cv_vs_alpha = -np.log10(ridgecv1.cv_values_)
    alphas = np.array(alpha_ridge)
    # plt.plot(m_log_alphas, ridgecv_rmse, ':')
    # plt.plot(m_log_alphas, ridgecv_rmse.mean(axis=-1), 'k', label='Average across the folds', linewidth=2)
    # plt.axvline(-np.log10(ridgecv.alpha_), linestyle='--', color='k', label='alpha: CV estimate')
    # for cvs in cv_vs_alpha:
    #    plt.plot(alphas, cvs, ':')
    # plt.plot(alphas, cv_vs_alpha.mean(axis=1), 'k', label='Average across the folds', linewidth=2)
    # plt.axvline(ridgecv.alpha_, linestyle='--', color='k', label='alpha: CV estimate')

    # plt.xlabel('-log(alpha)')
    # plt.ylabel('Root-mean-square error')
    # plt.title('Root-mean-square error on each fold: ' + name)
    # plt.legend()
    # plt.tight_layout()
    # plt.show()

    # Plot Fit vs DFT
    plt.figure()
    plt.scatter(ridge_energy, cluster_energy_ce, color="r", alpha=0.5)
    plt.plot(axis_range, axis_range, 'k', alpha=0.5)
    #plt.xlim(axis_range)
    #plt.ylim(axis_range)
    plt.gca().set_aspect('equal')
    plt.xlabel('Energy, DFT')
    plt.ylabel('Energy, CE')
    plt.title('RIDGE Fit Comparison: ' + name)
    #plt.tight_layout()
    plt.show()
    eahCE = [scale(comps[i], cluster_energy_ce[i], x1, y1, x2, y2) for i in range(len(cluster_energy_ce))]
    plt.scatter(eahDFT, eahCE, color='r', alpha=0.5)
    plt.plot(axis_rangeEAH, axis_rangeEAH, 'k', alpha=0.5)
    #plt.xlim(axis_rangeEAH)
    #plt.ylim(axis_rangeEAH)
    plt.gca().set_aspect('equal')
    plt.xlabel('EAH, DFT')
    plt.ylabel('EAH, CE')
    plt.title('RIDGE Fit Comparison: ' + name)
    #plt.tight_layout()
    plt.show()
    # Show Non-zero clusters
    cluster_coef = []
    cluster_pick = []
    cluster_coef.append(ridgecv1.intercept_)
    cluster_coef_all = ridgecv1.coef_
    cluster_nonzero = [c for c, v in enumerate(cluster_coef_all)]# if abs(v) >= 0.00000000001]
    for i in cluster_nonzero:
        cluster_coef.append(cluster_coef_all[i])
        cluster_pick.append(clusters[i])
    file.write("\n Clusters\n")
    for i in range(len(cluster_pick)):
        if len(cluster_pick[i]) == 2:
            file.write(str(cluster_pick[i][0]) + ':' + '[0]' + ':' + str(cluster_pick[i][1][0]) + ':' + str(
                cluster_coef[i + 1]) + '\n')
        else:
            file.write(
                str(cluster_pick[i][0]) + ':' + str(cluster_pick[i][1]) + ':' + str(cluster_pick[i][2][0]) + ':' + str(
                    cluster_coef[i + 1]) + '\n')

# Benchmarking and validation function.
def pert_test(clusters, energies, counts, comps, noise=0.1, Normalize=True, Intercept=True, Energy_above_hull = True, name=''):
    fold_pick = 10
    lasso_coefs = []
    ridge_coefs = []
    linreg_coefs = []
    counts = np.array(counts)
    energies = np.array(energies)
    ###- scale to energy above hull -###
    if Energy_above_hull == True:
        y1 = min(energies)
        y2 = max(energies)
        x2 = min(comps)
        x1 = max(comps)
        scale = lambda x0, y0, x1, y1, x2, y2: abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
            (y2 - y1) ** 2 + (x2 - x1) ** 2)
        energies = [scale(comps[i], energies[i], x1, y1, x2, y2) for i in range(len(energies))]

    ###- Set up output file -###
    file_out = 'pert_summery.txt'
    file = open(file_out, 'w')

    ###- Set up alphas for CV -###
    alpha_range = [-10, 10]
    alpha_lasso = np.logspace(alpha_range[0], alpha_range[1], num=1000)
    n_alphas = 1010
    alpha_ridge = np.logspace(-15, 10, n_alphas)

    # LASSO and RIDGE, Cross-Validation, Lin Reg without CV
    lassocv = LassoCV(alphas=alpha_lasso, normalize=Normalize, fit_intercept=Intercept, cv=fold_pick, max_iter=1e5)
    ridgecv = RidgeCV(alphas=alpha_ridge, normalize=Normalize, fit_intercept=Intercept, cv=None, store_cv_values=True)
    linreg = LinearRegression(fit_intercept=Intercept, normalize=Normalize)
    # Fit to data for each method
    noise = np.linspace(0.001,1,25)
    lasso_vars = [[] for _ in range(len(clusters))]
    for n in noise:
        lasso_coefs = []
        ridge_coefs = []
        linreg_coefs = []
        lassocv.fit(counts, energies)
        lasso_coefs.append(lassocv.coef_)
        ridgecv.fit(counts, energies)
        ridge_coefs.append(ridgecv.coef_)
        linreg.fit(counts, energies)
        linreg_coefs.append(linreg.coef_)
        for i in range(100):
            data_noise = np.random.normal(0, n, counts.shape)
            counts_new = counts + data_noise
            data_noise = np.random.normal(0, n, energies.shape)
            energies_new = energies + data_noise
            lassocv.fit(counts_new, energies_new)
            lasso_coefs.append(lassocv.coef_)
            ridgecv.fit(counts_new, energies_new)
            ridge_coefs.append(ridgecv.coef_)
            linreg.fit(counts_new, energies_new)
            linreg_coefs.append(linreg.coef_)
        lasso_coefs = np.array(lasso_coefs)
        ridge_coefs = np.array(ridge_coefs)
        linreg_coefs = np.array(linreg_coefs)
        for i in range(len(clusters)):
            data = np.transpose(lasso_coefs[:, i])
            var = data.var()
            lasso_vars[i].append(var)
    for i in range(len(lasso_vars)):
        plt.plot(noise,lasso_vars[i])
    file.close()
    return