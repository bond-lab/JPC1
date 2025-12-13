import wn, wn.ic
from wn.similarity import path, lin
import json
import os
from collections import defaultdict as dd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

###
### Instead of average depth, look at difference per pair src-tgt
###


# Suppress the numexpr warning if needed
import warnings
warnings.filterwarnings('ignore', message='.*numexpr.*')

data_dir = '../../example' #Chainnet directory
outdir = 'build'
os.makedirs(outdir, exist_ok=True)
log = open('related.log', 'w')
### store local copy of wordnets
os.makedirs('wn_data', exist_ok=True)
wn.config.data_directory = 'wn_data'

# Set Tufte-like style
sns.set_style("ticks", {
    'axes.linewidth': 0.5,
    'axes.edgecolor': '0.2',
    'grid.color': '0.9',
    'grid.linewidth': 0.5,
})
sns.set_context("paper", font_scale=1.1)
plt.rcParams['font.family'] = 'serif'


PAIRED_MEASURES = [
    ('depth', 'src_depth', 'tgt_depth', 'Depth'),
    ('synonyms', 'src_synonyms', 'tgt_synonyms', 'Synonyms'),
    ('abstract', 'src_abstract', 'tgt_abstract', 'Abstractness'),
]
TROPE_MEASURES = [
    ('src_depth', 'Source Depth'),
    ('tgt_depth', 'Target Depth'),
    ('src_synonyms', 'Source Synonyms'),
    ('tgt_synonyms', 'Target Synonyms'),
    ('src_abstract',  'Source  Abstractness'),
    ('tgt_abstract',  'Target  Abstractness'),
    ('path_distance', 'Path Distance'),
    ('depth_difference', 'Depth Difference'),
    ('abstract_difference', 'Abstract Difference'),
]

  



def read_data(data_dir, my_wn):
    """
    store all the tropes as a set
    (trope, word, source_sense_id, target_sense_id)
    """
    ### make mapping
    skey = dict()
    for s in my_wn.senses(pos='n'):
        skey[s.metadata()['identifier']] = s.id
    tropes = set()    
    # Read in metaphors
    with open(f"{data_dir}/chainnet_metaphor.json", "r") as fp:
        metaphor = json.load(fp)
    print('Read Metaphors')
    for e in metaphor['content']:
        w = e['wordform']
        fr_s = e['from_sense']
        to_s = e['to_sense']
        tropes.add(('metaphor', w, skey[fr_s], skey[to_s]))
    # Read in metonymy
    with open(f"{data_dir}/chainnet_metonymy.json", "r") as fp:
        metonymy = json.load(fp)
    print('Read Metonymy')
    for e in metonymy['content']:
        w = e['wordform']
        fr_s = e['from_sense']
        to_s = e['to_sense']
        tropes.add(('metonym', w, skey[fr_s], skey[to_s]))
    return tropes   

def measure_tropes(tropes, my_wn):
    """
    loop through the tropes and return some potentially interesting measures
    """
    #ic = wn.ic.load('~/nltk_data/corpora/wordnet_ic/ic-brown.dat', my_wn)
    
    scores = []
    for (trope, word, src_id, tgt_id) in tropes:
        s1 = my_wn.sense(id=src_id)
        s2 = my_wn.sense(id=tgt_id)
        ss1 = s1.synset()
        ss2 = s2.synset()
        
        path_dist = path(ss1, ss2)
#        lin_dist = path(ss1, ss2)  # Using path for now
        #lin_dist = lin(ss1, ss2, ic)
        
        scores.append({
            'trope': trope,
            'word': word,
            'src_depth': ss1.min_depth(),
            'tgt_depth': ss2.min_depth(),
            'src_topic': ss1.lexfile(),
            'tgt_topic': ss2.lexfile(),
            'src_synonyms': len(ss1.lemmas()),
            'tgt_synonyms': len(ss2.lemmas()),
            'src_abstract': get_abstractness(ss1, my_wn),
            'tgt_abstract': get_abstractness(ss2, my_wn),
            'path_distance': path_dist,
#            'lin_distance': lin_dist,
            'depth_difference': ss1.min_depth() - ss2.min_depth(),
            'abstract_difference': get_abstractness(ss1, my_wn) - get_abstractness(ss2, my_wn),
        })
    return pd.DataFrame(scores)

def get_abstractness(ss, my_wn):
    phys = my_wn.synsets(ili='i35546')[0]

    for p in ss.hypernym_paths():
        for s in p:
            if s == phys:
                return 0
    return 1


def perform_statistical_tests(df):
    """
    Perform statistical tests to compare metaphor and metonymy,
    and also compare source vs target within each trope type
    Returns dictionary of test results
    """
    meta_df = df[df['trope'] == 'metaphor']
    meto_df = df[df['trope'] == 'metonym']
    
    results = {
        'between_tropes': {},
        'within_tropes': {}
    }
    
    # Between-trope comparisons (metaphor vs metonymy)
   
    print("\n=== Between-Trope Comparisons (Metaphor vs Metonymy) ===")
    for col, label in TROPE_MEASURES:
        meta_vals = meta_df[col].dropna()
        meto_vals = meto_df[col].dropna()
        
        # Mann-Whitney U test
        u_stat, p_value_mw = stats.mannwhitneyu(meta_vals, meto_vals, alternative='two-sided')
        
        # t-test for comparison
        t_stat, p_value_t = stats.ttest_ind(meta_vals, meto_vals)
        
        # Effect size: Cohen's d
        pooled_std = np.sqrt((meta_vals.std()**2 + meto_vals.std()**2) / 2)
        cohens_d = (meta_vals.mean() - meto_vals.mean()) / pooled_std
        
        results['between_tropes'][col] = {
            'label': label,
            'mann_whitney_u': u_stat,
            'p_value_mw': p_value_mw,
            't_statistic': t_stat,
            'p_value_t': p_value_t,
            'cohens_d': cohens_d,
            'meta_mean': meta_vals.mean(),
            'meto_mean': meto_vals.mean(),
            # 'meta_median': meta_vals.median(),
            # 'meto_median': meto_vals.median()
        }
        
        print(f"\n{label}:")
        print(f"  Mann-Whitney U: U={u_stat:.1f}, p={p_value_mw:.4f}")
        print(f"  Cohen's d: {cohens_d:.3f}")
    
    # Within-trope comparisons (source vs target)
    print("\n=== Within-Trope Comparisons (Source vs Target) ===")
    
   
    for measure_name, src_col, tgt_col, label in PAIRED_MEASURES:
        print(measure_name, src_col, tgt_col, label)
        for trope_type, trope_df in [('metaphor', meta_df), ('metonym', meto_df)]:
            trope_name = 'Metaphor' if trope_type == 'metaphor' else 'Metonymy'
            
            src_vals = trope_df[src_col].dropna()
            tgt_vals = trope_df[tgt_col].dropna()
            
            # Wilcoxon signed-rank test (paired, non-parametric)
            w_stat, p_value_w = stats.wilcoxon(src_vals, tgt_vals, alternative='two-sided')
            
            # Paired t-test for comparison
            t_stat, p_value_pt = stats.ttest_rel(src_vals, tgt_vals)
            
            # Effect size for paired data: mean difference / SD of differences
            differences = src_vals - tgt_vals
            cohens_d = differences.mean() / differences.std()
            
            key = f"{trope_type}_{measure_name}"
            results['within_tropes'][key] = {
                'label': f"{trope_name} {label}",
                'trope': trope_name,
                'measure': label,
                'wilcoxon_w': w_stat,
                'p_value_w': p_value_w,
                't_statistic': t_stat,
                'p_value_pt': p_value_pt,
                'cohens_d': cohens_d,
                'src_mean': src_vals.mean(),
                'tgt_mean': tgt_vals.mean(),
                'mean_diff': differences.mean(),
                # 'src_median': src_vals.median(),
                # 'tgt_median': tgt_vals.median()
            }
            
            print(f"\n{trope_name} {label} (Source vs Target):")
            print(f"  Wilcoxon: W={w_stat:.1f}, p={p_value_w:.4f}")
            print(f"  Mean diff: {differences.mean():.3f}")
            print(f"  Cohen's d: {cohens_d:.3f}")
    
    return results

def create_comparison_plot_errorbar(df, src_col, tgt_col, ylabel, filename):
    """Create error bar plot comparing source and target for both trope types"""
    # Calculate statistics for each group
    stats = []
    for trope in ['metaphor', 'metonym']:
        trope_df = df[df['trope'] == trope]
        trope_name = 'Metaphor' if trope == 'metaphor' else 'Metonymy'
        
        for pos, col in [('Source', src_col), ('Target', tgt_col)]:
            stats.append({
                'Trope': trope_name,
                'Position': pos,
                'Mean': trope_df[col].mean(),
                'SD': trope_df[col].std(),
                'SE': trope_df[col].sem()
            })
    
    stats_df = pd.DataFrame(stats)
    
    print(f"\nCreating {filename} (error bar version)")
    print(stats_df)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Colors
    colors = {'Source': '#4878CF', 'Target': '#D65F5F'}
    
    # Plot error bars
    x_offset = {'Source': -0.15, 'Target': 0.15}
    
    for pos in ['Source', 'Target']:
        pos_data = stats_df[stats_df['Position'] == pos]
        x_positions = [0 + x_offset[pos], 1 + x_offset[pos]]
        
        ax.errorbar(x_positions, 
                   pos_data['Mean'].values,
                   yerr=pos_data['SD'].values,
                   fmt='o',
                   color=colors[pos],
                   markersize=6,
                   capsize=4,
                   capthick=1.5,
                   linewidth=1.5,
                   label=pos)
    
    # Tufte-like adjustments
    sns.despine(trim=True, offset=5)
    ax.set_ylabel(ylabel, fontweight='normal')
    ax.set_xlabel('')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Metaphor', 'Metonymy'])
    ax.legend(frameon=False, loc='best', title='')
    ax.grid(axis='y', alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(f"{outdir}/{filename}", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {filename}")

def create_distance_plots_errorbar(df):
    """Create error bar plots for path and lin distances"""
    for dist_type in ['path_distance',  'depth_difference',
                      'abstract_difference']:
        # Filter out None/NaN values
        valid_data = df[df[dist_type].notna()].copy()
        
        # Calculate statistics
        stats = []
        for trope in ['metaphor', 'metonym']:
            trope_df = valid_data[valid_data['trope'] == trope]
            trope_name = 'Metaphor' if trope == 'metaphor' else 'Metonymy'
            
            stats.append({
                'Trope': trope_name,
                'Mean': trope_df[dist_type].mean(),
                'SD': trope_df[dist_type].std(),
                'SE': trope_df[dist_type].sem()
            })
        
        stats_df = pd.DataFrame(stats)
        
        print(f"\nCreating {dist_type} plot (error bar version)")
        print(stats_df)
        
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Colors
        colors = {'Metaphor': '#6C8EBF', 'Metonymy': '#B85450'}
        
        # Plot error bars
        for i, row in stats_df.iterrows():
            ax.errorbar(i, 
                       row['Mean'],
                       yerr=row['SD'],
                       fmt='o',
                       color=colors[row['Trope']],
                       markersize=8,
                       capsize=5,
                       capthick=1.5,
                       linewidth=1.5)
        
        # Tufte-like adjustments
        sns.despine(trim=True, offset=5)
        dist_label = dist_type.replace('_', ' ').title()
        ax.set_ylabel(dist_label, fontweight='normal')
        ax.set_xlabel('')
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Metaphor', 'Metonymy'])
        ax.grid(axis='y', alpha=0.3, linewidth=0.5)
        
        plt.tight_layout()
        filename = f"{dist_type}_comparison_errorbar.png"
        plt.savefig(f"{outdir}/{filename}", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved {filename}")

def create_topic_heatmaps(df):
    """Create heatmaps showing source->target topic transitions"""
    for trope_type in ['metaphor', 'metonym']:
        trope_df = df[df['trope'] == trope_type].copy()
        
        if len(trope_df) == 0:
            continue
        
        # Create contingency table
        topic_matrix = pd.crosstab(
            trope_df['src_topic'], 
            trope_df['tgt_topic'],
            margins=False
        )
        
        # Only show topics that have at least 5 occurrences
        row_sums = topic_matrix.sum(axis=1)
        col_sums = topic_matrix.sum(axis=0)
        active_rows = row_sums[row_sums >= 5].index
        active_cols = col_sums[col_sums >= 5].index
        
        # Filter to active topics
        topic_matrix = topic_matrix.loc[active_rows, active_cols]
        
        if topic_matrix.empty:
            print(f"Not enough data for {trope_type} topic heatmap")
            continue
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create heatmap with muted colors
        sns.heatmap(topic_matrix, 
                    cmap='Blues', 
                    annot=True, 
                    fmt='d',
                    linewidths=0.5,
                    linecolor='white',
                    cbar_kws={'label': 'Count'},
                    ax=ax)
        
        # Tufte-like adjustments
        ax.set_xlabel('Target Topic', fontweight='normal')
        ax.set_ylabel('Source Topic', fontweight='normal')
        
        trope_name = 'Metaphor' if trope_type == 'metaphor' else 'Metonymy'
        ax.set_title(f'{trope_name} Topic Transitions', 
                     fontweight='normal', pad=20)
        
        plt.tight_layout()
        filename = f"{trope_type}_topic_heatmap.png"
        plt.savefig(f"{outdir}/{filename}", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved {filename}")

def interpret_effect_size(d):
    """Interpret Cohen's d effect size"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

def format_p_value(p):
    """Format p-value for LaTeX"""
    if p < 0.001:
        return "$p < .001$"
    elif p < 0.01:
        return f"$p = {p:.3f}$"
    else:
        return f"$p = {p:.2f}$"

def generate_latex_summary(df, test_results):
    """Generate LaTeX tables with summary statistics and test results"""
    
    # Split by trope type
    meta_df = df[df['trope'] == 'metaphor']
    meto_df = df[df['trope'] == 'metonym']
    
    latex_output = []
    
    # Summary statistics table with both mean and median
    latex_output.append("% Summary Statistics by Trope Type")
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append("\\caption{Descriptive Statistics for Metaphor and Metonymy}")
    latex_output.append("\\label{tab:stats}")
    latex_output.append("\\begin{tabular}{lrrrrrr}")
    latex_output.append("\\toprule")
    latex_output.append("Measure & \\multicolumn{3}{c}{Metaphor} & \\multicolumn{3}{c}{Metonymy} \\\\")
    latex_output.append("\\cmidrule(lr){2-4} \\cmidrule(lr){5-7}")
    latex_output.append("        & Mean &  SD & IQR & Mean  SD & IQR \\\\")
    latex_output.append("\\midrule")
    
    for col, label in TROPE_MEASURES:
        meta_mean = meta_df[col].mean()
        meta_median = meta_df[col].median()
        meta_sd = meta_df[col].std()
        meta_iqr = meta_df[col].quantile(0.75) - meta_df[col].quantile(0.25)
        
        meto_mean = meto_df[col].mean()
#        meto_median = meto_df[col].median()
        meto_sd = meto_df[col].std()
        meto_iqr = meto_df[col].quantile(0.75) - meto_df[col].quantile(0.25)
        
        latex_output.append(f"{label} & {meta_mean:.2f}  & {meta_sd:.2f} & {meta_iqr:.2f} & "
                          f"{meto_mean:.2f}  & {meto_sd:.2f} & {meto_iqr:.2f} \\\\")
    
    latex_output.append("\\midrule")
    latex_output.append(f"N & \\multicolumn{{3}}{{c}}{{{len(meta_df)}}} & \\multicolumn{{3}}{{c}}{{{len(meto_df)}}} \\\\")
    latex_output.append("\\bottomrule")
    latex_output.append("\\end{tabular}")
    latex_output.append("\\end{table}")
    latex_output.append("")
    
    # Between-trope statistical tests table
    latex_output.append("% Statistical Tests: Between Tropes (Metaphor vs Metonymy)")
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append("\\caption{Statistical Comparison: Metaphor vs Metonymy}")
    latex_output.append("\\label{tab:between}")
    latex_output.append("\\begin{tabular}{lrrr}")
    latex_output.append("\\toprule")
    latex_output.append("Measure & Mann-Whitney $U$ & Cohen's $d$ & Effect Size \\\\")
    latex_output.append("\\midrule")
    
    for col, label in TROPE_MEASURES:
        result = test_results['between_tropes'][col]
        p_formatted = format_p_value(result['p_value_mw'])
        effect = interpret_effect_size(result['cohens_d'])
        
        latex_output.append(f"{result['label']} & {p_formatted} & {result['cohens_d']:.3f} & {effect} \\\\")
    
    latex_output.append("\\bottomrule")
    latex_output.append("\\end{tabular}")
    latex_output.append("\\end{table}")
    latex_output.append("")
    
    # Within-trope statistical tests table (source vs target)
    latex_output.append("% Statistical Tests: Within Tropes (Source vs Target)")
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append("\\caption{Statistical Comparison: Source vs Target within Trope Types}")
    latex_output.append("\\label{tab:within}")
    latex_output.append("\\begin{tabular}{lrrrr}")
    latex_output.append("\\toprule")
    latex_output.append("Comparison & Mean Diff & Wilcoxon & Cohen's $d$ & Effect Size \\\\")
    latex_output.append("\\midrule")
    
    within_order = ['metaphor_depth', 'metaphor_synonyms',
                    'metaphor_abstract',
                    'metonym_depth', 'metonym_synonyms',
                    'metonym_abstract',    ]
    for key in within_order:
        if key in test_results['within_tropes']:
            result = test_results['within_tropes'][key]
            p_formatted = format_p_value(result['p_value_w'])
            effect = interpret_effect_size(result['cohens_d'])
            
            latex_output.append(f"{result['label']} & {result['mean_diff']:.2f} & {p_formatted} & "
                              f"{result['cohens_d']:.3f} & {effect} \\\\")
    
    latex_output.append("\\bottomrule")
    latex_output.append("\\end{tabular}")
    latex_output.append("\\end{table}")
    latex_output.append("")
    
    # Statistical methods description
    latex_output.append("% Statistical Methods")
    latex_output.append("\\subsection*{Statistical Methods}")
    latex_output.append("")
    latex_output.append("\\paragraph{Between-Trope Comparisons}")
    latex_output.append("We compared metaphor and metonymy using the Mann-Whitney $U$ test, ")
    latex_output.append("a non-parametric test appropriate for comparing two independent samples ")
    latex_output.append("without assuming normal distributions. Given the large sample sizes ")
    latex_output.append(f"($n_{{{{metaphor}}}} = {len(meta_df)}$, $n_{{{{metonymy}}}} = {len(meto_df)}$), ")
    latex_output.append("this test provides robust results even with skewed distributions.")
    latex_output.append("")
    
    latex_output.append("\\paragraph{Within-Trope Comparisons}")
    latex_output.append("To compare source and target synsets within each trope type, ")
    latex_output.append("we used the Wilcoxon signed-rank test, a non-parametric paired test ")
    latex_output.append("that does not assume normal distributions. This test is appropriate because ")
    latex_output.append("each trope instance provides a natural pairing of source and target synsets.")
    latex_output.append("")
    
    latex_output.append("\\paragraph{Effect Sizes}")
    latex_output.append("We report Cohen's $d$ as a standardized measure of effect size, ")
    latex_output.append("interpreted as: negligible ($|d| < 0.2$), small ($0.2 \\leq |d| < 0.5$), ")
    latex_output.append("medium ($0.5 \\leq |d| < 0.8$), or large ($|d| \\geq 0.8$). ")
    latex_output.append("For between-trope comparisons, positive values indicate metaphor has higher values; ")
    latex_output.append("for within-trope comparisons, positive values indicate source has higher values than target.")
    latex_output.append("")
    
    # Key findings - between tropes
    latex_output.append("\\paragraph{Key Findings: Between Tropes}")
    
    significant_between = [(col, res) for col, res in test_results['between_tropes'].items() 
                          if res['p_value_mw'] < 0.001]
    
    if significant_between:
        latex_output.append("Statistically significant differences ($p < .001$) between metaphor and metonymy:")
        latex_output.append("\\begin{itemize}")
        for col, res in significant_between:
            direction = "higher" if res['meta_mean'] > res['meto_mean'] else "lower"
            latex_output.append(f"  \\item \\textbf{{{res['label']}}}: "
                              f"Metaphor shows {direction} values "
                              f"(Cohen's $d = {res['cohens_d']:.3f}$, {interpret_effect_size(res['cohens_d'])} effect).")
        latex_output.append("\\end{itemize}")
    latex_output.append("")
    
    # Key findings - within tropes
    latex_output.append("\\paragraph{Key Findings: Source vs Target}")
    
    significant_within = [(key, res) for key, res in test_results['within_tropes'].items() 
                         if res['p_value_w'] < 0.001]
    
    if significant_within:
        latex_output.append("Statistically significant differences ($p < .001$) between source and target:")
        latex_output.append("\\begin{itemize}")
        for key, res in significant_within:
            direction = "higher" if res['mean_diff'] > 0 else "lower"
            latex_output.append(f"  \\item \\textbf{{{res['label']}}}: "
                              f"Source shows {direction} values than target "
                              f"(mean diff = {res['mean_diff']:.2f}, "
                              f"Cohen's $d = {res['cohens_d']:.3f}$, {interpret_effect_size(res['cohens_d'])} effect).")
        latex_output.append("\\end{itemize}")
    latex_output.append("")
    
    # Top topic transitions table for metaphor
    latex_output.append("% Top Topic Transitions for Metaphor")
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append("\\caption{Most Frequent Topic Transitions in Metaphor (Top 15)}")
    latex_output.append("\\begin{tabular}{llr}")
    latex_output.append("\\toprule")
    latex_output.append("Source Topic & Target Topic & Count \\\\")
    latex_output.append("\\midrule")
    
    meta_transitions = meta_df.groupby(['src_topic', 'tgt_topic']).size().sort_values(ascending=False).head(15)
    for (src, tgt), count in meta_transitions.items():
        src_clean = src.replace('_', '\\_')
        tgt_clean = tgt.replace('_', '\\_')
        latex_output.append(f"{src_clean} & {tgt_clean} & {count} \\\\")
    
    latex_output.append("\\bottomrule")
    latex_output.append("\\end{tabular}")
    latex_output.append("\\end{table}")
    latex_output.append("")
    
    # Top topic transitions table for metonymy
    latex_output.append("% Top Topic Transitions for Metonymy")
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append("\\caption{Most Frequent Topic Transitions in Metonymy (Top 15)}")
    latex_output.append("\\begin{tabular}{llr}")
    latex_output.append("\\toprule")
    latex_output.append("Source Topic & Target Topic & Count \\\\")
    latex_output.append("\\midrule")
    
    meto_transitions = meto_df.groupby(['src_topic', 'tgt_topic']).size().sort_values(ascending=False).head(15)
    for (src, tgt), count in meto_transitions.items():
        src_clean = src.replace('_', '\\_')
        tgt_clean = tgt.replace('_', '\\_')
        latex_output.append(f"{src_clean} & {tgt_clean} & {count} \\\\")
    
    latex_output.append("\\bottomrule")
    latex_output.append("\\end{tabular}")
    latex_output.append("\\end{table}")
    
    # Write to file
    with open(f"{outdir}/summary_tables.tex", 'w') as f:
        f.write('\n'.join(latex_output))
    
    print(f"\nSaved LaTeX summary tables to {outdir}/summary_tables.tex")

if __name__ == "__main__":
    print('Downloading OMW 1.4')
    wn.download('omw-en:1.4')
    ewn = wn.Wordnet(lexicon='omw-en:1.4')
    
    print('Reading trope data...')
    tropes = read_data(data_dir, ewn)
    print(f"Found {len(tropes)} tropes")
    
    print('Measuring tropes...')
    df = measure_tropes(tropes, ewn)
    
    # Save raw data
    df.to_csv(f"{outdir}/trope_measurements.csv", index=False)
    print(f"Saved measurements for {len(df)} tropes")
    
    # Perform statistical tests

    print('\nPerforming statistical tests...')
    test_results = perform_statistical_tests(df)
    
    # Create visualizations - error bar version
    print('\nCreating error bar visualizations...')
    create_comparison_plot_errorbar(df, 'src_depth', 'tgt_depth', 
                          'Min Depth', 'depth_comparison_errorbar.png')
    create_comparison_plot_errorbar(df, 'src_synonyms', 'tgt_synonyms', 
                          'Number of Synonyms', 'synonyms_comparison_errorbar.png')
    create_comparison_plot_errorbar(df, 'src_abstract', 'tgt_abstract', 
                                    'Abstractness', 'abstract_comparison_errorbar.png')
   
    create_distance_plots_errorbar(df)
    
    # Create topic heatmaps
    print('\nCreating topic heatmaps...')
    create_topic_heatmaps(df)
    
    # Generate LaTeX summary
    print('\nGenerating LaTeX summary...')
    generate_latex_summary(df, test_results)
    
    print('\nDone!')
    log.close()
