from pathlib import PosixPath as Path
from itertools import permutations

import pandas as pd
import numpy as np
import plotly.offline as ply
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#TODO: "standardize" logging format and setup within the app?
import logging
log = logging.getLogger('plots')
log_format = '%(levelname)s in "%(name)s" on %(lineno)d: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

from runqc.utils import get_file_paths
from runqc.plotly_config import plotly_config #, orca_config


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Pipeline Globals ~~~~~
PIPELINE_FILE_GLOB = 'pipe_16S_QC-*.csv'
PIPELINE_PCTS_GLOB = 'pipe_16S_spike_pcts-*.tsv'

# set float display to integer only, as no floats included in qc logs (default format = None)
pd.options.display.float_format = '{:,.0f}'.format

plot_opts = dict(
    auto_open = False,
    # image = 'svg', # only for automatic downloads
    image_width = 1000,
    output_type = 'div',
    include_plotlyjs = False,
    config = plotly_config,
)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Plot Methods ~~~~~

def parse_project_name(filename):
    """parse project name from (expected!) filename
        "pipe_16S_QC-<proj>-<flow>.csv"
    """
    try:
        if filename.endswith('.csv'):
            filename.rstrip('.csv')
        parts = filename.split('-')
        return parts[2]
    except Exception as e:
        return filename


def find_pipeline_qc_files(folder_path, fileglob=PIPELINE_FILE_GLOB):
    """return list of all existing files from the 16S pipeline's QC logs"""
    try:
        log.info('Finding pipeline QC files')
        pipe_files = get_file_paths(folder_path, fileglob=fileglob)
    except Exception as e:
        log.exception('Issues finding pipeline files in "%s"', folder_path)
        raise e
    else:
        log.debug('found %s pipeline qc files', len(pipe_files))
        return pipe_files


def layout_axis_defaults(axis_title=''):
    """return dict of default layout settings"""
    axis_defaults = dict(
        title = axis_title,
        visible = True,
        color = 'Black',
        showgrid = True,

        linecolor = '#444',
        linewidth = 2,
        zeroline = True,
        showline = True,
        mirror = True,

        automargin = True,
        autorange = True,
        rangemode = "nonnegative",

        showticklabels = True,
        ticks = 'outside',
        tickmode = 'auto',
        tickangle = 45,
        ticklen = 5,
        tickwidth = 2,

        showspikes = True,
        spikethickness = 2,
        spikedash = 'dot',
        spikemode = 'across',

        hoverformat = '.0f', # don't use exponents
    )
    return axis_defaults


def make_layout(title='', bgcolor='aliceblue', fontsize=12):
    """return plotly Layout object with default settings.
    The object returned can be modified as needed.
    """
    try:
        log.debug('make_layout: axes')
        layout_xaxis = layout_axis_defaults()
        layout_yaxis = layout_axis_defaults()

        log.debug('make_layout: legend')
        layout_legend = dict(
            bgcolor = 'white',
            bordercolor = 'Black',
            borderwidth = 1,
            orientation = 'v',
            x = 0.80,
            xanchor = 'center',
            y = 0.90,
            yanchor = 'top',
            traceorder = 'normal',
        )

        log.debug('make_layout: margins')
        layout_margins = dict(
            l = 5,  r = 5,
            t = 65, b = 5,
            pad = 0,
            autoexpand = True
        )

        log.debug('make_layout: object')
        layout = go.Layout(
            font = dict(size=fontsize),
            plot_bgcolor = bgcolor,
            title = title,
            autosize = True,
            hidesources = True,
            hovermode = 'y',
            dragmode = 'pan',
            showlegend = True,
            legend = layout_legend,
            margin = layout_margins,
            xaxis = layout_xaxis,
            yaxis = layout_yaxis,
        )
        # log.debug('made layout: %s', str(layout))
    except Exception as e:
        log.exception('make_layout NOT made!!')
        raise e
    else:
        return layout


def plot_bar_chart(fp, df):
    """create bar chart from passed dataframe, then save result in fp.parent
    params:
        fp: Path of data file
        df: pandas dataframe
    """
    try:
        log.info('Creating bar chart for %s', fp.name)

        image_name = fp.stem #+ '.svg'

        try:
            log.debug('bar_chart: gonna set display vars')

            colors = [
                'YellowGreen', 'Chocolate',
                'LightSteelBlue', 'LightCoral', 'OliveDrab',
                'DarkSlateBlue', 'Plum', 'Teal', 'Silver',
            ]
            marker_line = {'color': 'Black',
                           'width': 1 }
        except Exception as e:
            log.exception('bar_chart: display variables NOT set')
            raise e

        try:
            log.debug('bar_chart: gonna make layout')
            layout_title_text = ''.join([
                'Project ',
                parse_project_name(fp.stem),
                ' Read Counts ',
                ' <a style="font-size: 0.7em" href="', fp.name, '" download>',
                '[download ', fp.suffix[1:], ' file]',
                '</a>'
            ])
            layout_title = dict(text=layout_title_text, font={'color':'SteelBlue'})
            layout = make_layout(title=layout_title)

            log.debug('bar_chart: gonna modify layout specs')
            layout.barmode = 'stack'

            # height = number of records plus top and bottom margins
            plot_height = df.index.size * 25 \
                          + layout.margin['t'] \
                          + layout.margin['b']
            layout.height = plot_height

            log.debug('bar_chart: gonna modify layout spec: xaxis')
            layout.xaxis.update(dict(
                # title = 'Number of Reads',
                ticksuffix = ' reads',
                tickangle = -3,
                side = 'top',
            ))

            log.debug('bar_chart: gonna modify layout spec: yaxis')
            text_max_len = 40
            y_ticktexts = []
            for n in df.index:
                y_ticktexts.append(
                    n if len(n)<text_max_len
                    else n[0:text_max_len]+u'\u2026' # ellipsis
                )
            layout.yaxis.update(dict(
                showspikes = False,
                mirror = False,
                tickangle = 0,
                tickmode = 'array',
                tickvals = df.index,
                ticktext = y_ticktexts,
            ))

            log.debug('bar_chart: layout variables set')
            # log.debug('bar_chart: layout: %s', str(layout))
        except Exception as e:
            log.exception('bar_chart: layout NOT made')
            raise e

        try:
            log.debug('bar_chart: gonna create annotations right side column "total" reads')
            annotations = []
            annot_defaults = dict(
                font = {'size': 11, 'color': 'Black'},
                align = 'right',
                bgcolor = 'WhiteSmoke',
                borderwidth = 0,
                borderpad = 1,
                showarrow = False,
                xanchor = 'right',
                xref = 'paper',
                x = 1,
                yref = 'y',
            )
            # pop column 'total' values for annotation display
            for row_num, total in enumerate(df.pop('total')):
                annotations.append(dict(
                    **annot_defaults,
                    text = f'<b>{total}</b>',
                    y = row_num,
                ))
            log.debug('bar_chart: gonna create total column label annotation')
            annotations.append(dict(
                text = '<b>All Reads</b>',
                textangle = 0,
                font = {'size': 11, 'color': 'RoyalBlue'},
                align = 'center',
                bgcolor = 'WhiteSmoke',
                bordercolor = 'Black',
                borderpad = 2,
                showarrow = False,
                xanchor = 'right',
                xref = 'paper',
                x = 1,
                xshift = 5,
                yanchor = 'bottom',
                yref = 'paper',
                y = 1,
                yshift = 5,
            ))

            log.debug('bar_chart: gonna assign layout annotations')
            layout['annotations'] = annotations
        except Exception as e:
            log.exception('bar_chart: layout annotations NOT made')
            raise e

        try:
            log.debug('bar_chart: gonna make data traces')
            data = []
            for i in range(df.columns.size):
                colname = df.columns[i]
                # log.debug('bar_chart: column: %s', colname)
                bar = go.Bar(
                    orientation = 'h',
                    name = colname,
                    hoverinfo = "x+name",
                    marker = {'color': colors[i],
                              'line': marker_line},
                    x = df[colname],
                    y = df.index,
                    text = df[colname],
                    textposition = 'inside', 
                    textfont = {'size': 14,
                                'color': 'Black'},
                )
                data.append(bar)
            # log.debug('bar_chart: data: %s', str(data))
        except Exception as e:
            log.exception('bar_chart: data traces NOT made')
            raise e

        try:
            log.debug('bar_chart: gonna make figure')
            fig = go.Figure(data=data, layout=layout)
            # log.debug('bar_chart: figure %s', str(fig.__dict__))
        except Exception as e:
            log.exception('bar_chart: figure')
            raise e

        try:
            log.debug('bar_chart: gonna make plot')
            plotly_config['modeBarButtonsToRemove'] = ['toggleSpikelines',
                                                       # 'sendDataToCloud',
                                                       'lasso']

            plot_opts['config']['toImageButtonOptions']['filename'] = image_name
            plot = ply.plot(fig, **plot_opts)
        except Exception as e:
            log.exception('bar_chart: plot not working')
            raise e

    except Exception as e:
        log.exception('bar_chart: plotting for file "%s"', fp.name)
        raise e
    else:
       return plot


def calc_read_diffs(df_orig, columns=[]):
    """Caclulate differences between steps of pipeline, return new dataframe"""
    if not columns:
        # expected columns = ['raw', 'trimmed', 'combined', 'nonchimera', 'nonhost']
        columns = df.columns
    diffcols = ['final', 'host', 'chimera', 'uncombined', 'trimmed', 'total']

    try:
        diff_df = pd.DataFrame(columns=diffcols, dtype='int64')
        diff_df.total      = df_orig.raw
        diff_df.final      = df_orig.nonhost
        diff_df.host       = df_orig.eval('nonchimera - nonhost')
        diff_df.chimera    = df_orig.eval('combined - nonchimera')
        diff_df.uncombined = df_orig.eval('trimmed - combined')
        diff_df.trimmed    = df_orig.eval('raw - trimmed')
    except Exception as e:
        log.exception('Issues getting diffs from "%s"', )
        raise e
    finally:
        return diff_df


def plot_16S_read_counts(run_path, flowcell=None, sort_by='nonhost'):
    """if 16S pipeline's log of number of reads deleted from each step exists,
       then create plots from the csv data within.
       Return the plotly-specific interactive output, or only the svg data.
    """
    log.info('Plotting 16S pipeline QC')
    plot_map = {} # e.g. {'file.name': 'path to plotly output html file or svg image'}
    try:
        # check file(s) exist / find files by glob suffix .csv
        try:
            fpaths = find_pipeline_qc_files(run_path)
            # log.debug('plot_16S: fpaths: %s', str(fpaths))
        except Exception as e:
            log.exception('Issues finding files in "%s"', run_path)
            raise e

        try:
            # read contents of each filepath
            # pipe logs have header:
            #       Sample_name,QC_raw,QC_trim,QC_combined,QC_nonchimera,QC_nonhost
            # Renamed here for plot display:
            readcnts = ['raw', 'trimmed', 'combined', 'nonchimera', 'nonhost']
            colnames = ['Sample_Name'] + readcnts
            log.debug('plot_16S: colnames=%s', str(colnames))
            for fp in fpaths:
                df_read = pd.read_csv(fp, header=0, names=colnames, index_col=0)
                # replace non-numeric values e.g. 'Missing' with zeros
                df = df_read.replace(regex='^.*[^\d].*$', value='0')
                # exclude NaN indexed sample names (missing, empty fields)
                df = df.loc[df.index.notna()]
                # re-convert all 'object' dtypes to 'int'
                astypes = {col: int for col in df.columns[1:]}
                df = df.astype(astypes)

                # log.debug('plot_16S: df.columns=%s', str(df.columns))
                if sort_by:
                    df.sort_values(by=sort_by, ascending=True, inplace=True)

                try: # calc num reads removed in each pipe step
                    df = calc_read_diffs(df, columns=readcnts)
                except Exception as e:
                    log.exception('Issues calcing read diffs: file "%s" in "%s"', fp.name, run_path)
                try: # create stacked bar plots
                    fp_bar = plot_bar_chart(fp, df)
                except Exception as e:
                    log.exception('Issues plotting bar: file "%s" in "%s"', fp.name, run_path)
                else:
                    plot_map[fp.stem] = fp_bar

        except Exception as e:
            log.exception('Issues plotting qc files in "%s"', run_path)
            raise e

    except Exception as e:
        log.exception('Issues in plot_16S in "%s"', run_path)
        raise e
    finally:
        log.info('Plotted %s ', len(plot_map.keys()))
        return plot_map


def plot_scatter_chart(fp, df, name=''):
    """create scatter chart from passed dataframe, return list of resulting traces.
    params:
        fp:  Path of data file
        df:  pandas dataframe
            Note: using only x=index and y=first-column
        name: trace name (in legend)
    """
    try:
        log.info('Creating scatter chart for %s', fp.name)
        try:
            log.debug('scatter_chart: gonna make data traces')
            colors = ['OliveDrab', 'YellowGreen', 'Chocolate']
            markers = {'color': colors[0],
                       'size': 5,
                       'symbol': "circle-dot",
                       }
            colname = df.columns[0]
            log.debug(f'scatter_chart: y={colname}')
            scat = go.Scatter(
                x = df.index,
                y = df[colname],
                mode = 'markers',
                hoverinfo = "x+y",
                marker = markers,
                name = name,
            )
        except Exception as e:
            log.exception('scatter_chart: data traces NOT made')
            raise e
        else:
            return scat
    except Exception as e:
        log.exception('scatter_chart: plotting for file "%s"', fp.name)
        raise e


def plot_spike_pcts(run_path, compare_columns=[]):
    """if 16S pipeline's file with percent of spike reads exists:
       then create scatter plots from the tsv data within.
       Return the plotly-specific interactive output, or only the svg data.
       params:
         run_path: Path of sequencer run
         compare_columns list: [colname, col2, ...] to compare by division
    """
    log.info('Plotting 16S pipeline pct reads of spikes')
    # pre-create dict of file paths:
    plot_map = {} # e.g. {'file.name': 'path to plotly output html file or svg image'}
    try:
        # check file(s) exist / find files by glob suffix .csv
        try:
            fpaths = find_pipeline_qc_files(run_path, fileglob=PIPELINE_PCTS_GLOB)
            # log.debug('plot_16S: fpaths: %s', str(fpaths))
        except Exception as e:
            log.exception('Issues finding files in "%s"', run_path)
            raise e

        try:
            if fpaths:
                log.debug('spike pcts: goint to scatter')
            else:
                log.debug('spike pcts: no files found')
                return plot_map

            for fp in fpaths:
                try: # is it empty?
                    s = fp.stat().st_size
                    if s==0:
                        continue
                except: # is it unreadable?
                    continue

                # pipe tsv's have no header line e.g. data:
                # AZMA_J00T4S_1_XC...	OTU_Allobacillus	.13651877133105802000%	21	21340
                colnames = ['SampleName', 'SpikeName', 'PctReads', 'SpikeReads', 'TotalReads']
                # log.debug('plot_spikes: colnames=%s', str(colnames))

                """determine rows and cols for 'specs' of subplots; dependent on compares"""
                fig_title = 'Sample Reads vs % Spike Reads'
                num_rows = 1
                num_cols = 1
                plot_height = 350
                if compare_columns:
                    num_rows+=1
                    plot_height = 800
                    comp_names = tuple({f'{p0} vs {p1}'
                                        for p0,p1 in
                                        permutations(compare_columns, r=2)})
                    num_cols = len( comp_names )
                    sub_titles = (fig_title,) + comp_names

                    firstrow = [{'rowspan':1, 'colspan':num_cols}]
                    firstrow += [None for c in range(1, num_cols)]
                    fig_spec = [firstrow]

                    coldicts = [{} for c in range(num_cols)]
                    fig_spec.extend([ coldicts for r in range(1, num_rows) ])
                    # log.debug(f'fig subplot spec: {fig_spec}')
                else:
                    fig_spec = [[{}]]
                    sub_titles = (fig_title,)

                log.warning(f'fig sub_titles: {sub_titles}')
                fig = make_subplots(rows=num_rows,
                                    cols=num_cols,
                                    subplot_titles=sub_titles,
                                    specs=fig_spec,
                                    print_grid=True
                                    )

                sub_axes_opts = dict(
                    type = 'linear',
                    rangemode = 'tozero',
                    linecolor = 'black',
                    linewidth = 1,
                    zeroline = True,
                    showline = True,
                    mirror = True,
                    showticklabels = True,
                    ticks = 'outside',
                    tickmode = 'auto',
                    tickangle = 45,
                    ticklen = 5,
                    tickwidth = 2,
                    nticks = 11,
                )

                """Gen DataFrame from tsv file"""
                log.debug('Reading spike tsv file.')
                df = pd.read_csv(fp, names=colnames, sep='\t')

                # remove % signs from PctReads column, convert to float
                df['PctReads'] = df['PctReads'].str.replace('%$', '', regex=True).astype(float)

                # pivot the data to calc % and total spike reads
                df_pivot = df.pivot_table(index=['SampleName','TotalReads'],
                                          columns='SpikeName', values='PctReads',
                                          fill_value=0, aggfunc=np.sum,
                                          margins=True, margins_name='TotalPct')
                df_pivot.reset_index(level='TotalReads', inplace=True) # move index to col

                df_reads = df.pivot_table(index='SampleName', columns='SpikeName',
                                          values='SpikeReads', fill_value=0)
                df_pivot['TotalSpikeReads'] = df_reads.agg(sum, axis=1) # sum all spikes' reads

                try: # create total reads/pcts scatter charts
                    df_totals = df_pivot.filter(['TotalReads','TotalPct'])
                    df_totals.set_index('TotalPct', inplace=True)
                    fp_scatter = plot_scatter_chart(fp, df_totals)
                except Exception:
                    log.exception('Issues plotting scatter: file "%s" in "%s"', fp.name, run_path)
                else:
                    fig.add_trace(fp_scatter, row=1, col=1)
                    fig.update_xaxes(row=1, col=1,
                                     title_text='% Spike Reads',
                                     ticksuffix='%',
                                     **sub_axes_opts
                                    )
                    fig.update_yaxes(row=1, col=1,
                                     title_text='Sample Reads',
                                     **sub_axes_opts
                                     )

                if compare_columns:
                    try: # create comparison scatter charts
                        #NOTE: Requires compare_columns elements to hold existing key Names of cols!
                        #TODO: check items in compare_columns matching values in SpikeNames
                        df_comp = df_pivot.filter(items=compare_columns)

                log.debug('scatter_chart: gonna write pivoted data file')
                fp_pivot = fp.with_suffix('.pivot.csv')
                if not fp_pivot.exists():
                    df_pivot.to_csv(fp_pivot, header=True, index=True,
                                    chunksize=df.shape[1]/5)

                        for num, comps in enumerate( permutations(compare_columns, r=2), 1 ):
                            cmp_div = df_comp[comps[0]]/df_comp[comps[1]]
                            df_div = pd.DataFrame(cmp_div)
                            fp_scatter = plot_scatter_chart(fp, df_div)
                            fig.add_trace(fp_scatter, row=2, col=num)
                            fig.update_xaxes(row=2, col=num, **sub_axes_opts)
                            fig.update_yaxes(row=2, col=num, **sub_axes_opts)

                    except Exception:
                        log.exception('Issues comparing spikes: file "%s" in "%s"', fp.name, run_path)

                log.debug('fig.layout: layout title')
                layout_title_text = ''.join([
                    f'Project {parse_project_name(fp.stem)!s} Spike Reads',
                    ' <a style="font-size: 0.7em" href="', fp_pivot.name, '" download>',
                    '[download ', fp_pivot.suffix[1:], ' file]',
                    '</a>'
                ])
                layout_title = dict(text=layout_title_text, font={'color':'SteelBlue'})
                fig.layout.title = layout_title
                fig.layout.showlegend = False
                # log.debug(f'fig.layout: {fig.layout}')

                # log.debug(f'fig json: {fig.to_plotly_json()}')
                try:
                    log.debug('scatter_chart: gonna make plot')

                    img_path = fp.with_suffix('.scatter')
                    plot_opts['config']['toImageButtonOptions']['filename'] = img_path.name
                    plot = ply.plot(fig, **plot_opts)
                    log.debug('scatter_chart: made scatter plot!')
                except Exception as e:
                    log.exception('scatter_chart: plot not working')
                    raise e
                else:
                    plot_map[fp.stem] = plot

        except Exception as e:
            log.exception('Issues plotting qc files in "%s"', run_path)
            raise e

    except Exception as e:
        log.exception('Issues in plot_16S in "%s"', run_path)
        raise e
    finally:
        log.info('Plotted %s ', len(plot_map.keys()))
        return plot_map


if __name__ == '__main__':
    try: # base tests
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            plot_opts = dict(
                output_type = 'div',
                include_plotlyjs = False,
                config = plotly_config,
            )

            run_abspath = Path('/var/www/apps/run_qc_devel/runs/20180605_18-microbe-027_BNYKP_qc')
            flowcell = 'BNYL2'
            # pipeline_16S_qc_plots = plot_16S_read_counts(run_abspath, flowcell)
            # print(f'pipeline_16S_qc_plots: {pipeline_16S_qc_plots!s}')

            run_abspath = Path('/var/www/apps/run_qc_devel/runs/20190909_19-microbe-028_CJJ4V_qc')
            flowcell = 'CJJ4V'
            comp_cols = [ 'OTU_Allobacillus', 'OTU_Imtechella' ]
            # plot_spikes = plot_spike_pcts(run_abspath, compare_columns=['otu1', 'otu3'])
            plot_spikes = plot_spike_pcts(run_abspath, compare_columns=comp_cols)
            # plot_spikes = plot_spike_pcts(run_abspath)
            log.debug(layout_axis_defaults(axis_title='', title='Ttle', auto_margins=False))

    except Exception as e:
        log.exception('issues plotting bar charts for run')
        raise e
