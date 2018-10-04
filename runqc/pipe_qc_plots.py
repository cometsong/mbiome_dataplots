from pathlib import PosixPath as Path
import csv

import pandas as pd
import plotly.offline as ply
import plotly.graph_objs as go

#TODO: "standardize" logging format and setup within the app?
import logging
log = logging.getLogger('plots')
log_format = '%(levelname)s in "%(name)s" on %(lineno)d: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

from runqc.utils import get_file_paths
from runqc.plotly_config import plotly_config


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Pipeline Globals ~~~~~
PIPELINE_FILE_GLOB = 'pipe_16S_QC-*.csv'

# set float display to integer only, as no floats included in qc logs (default format = None)
pd.options.display.float_format = '{:,.0f}'.format

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
        log.error('Issues finding pipeline files in "%s"', run_path)
        raise e
    else:
        log.debug('found %s pipeline qc files', len(pipe_files))
        return pipe_files


def layout_axis_defaults(axis_title=''):
    """return dict of default layout settings"""
    axis_defaults = dict(
        title = axis_title,
        visible = True,
        color = 'black',
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
            bordercolor = 'black',
            borderwidth = 1,
            orientation = 'v',
            x = 0.975,
            xanchor = 'right',
            y = 0.925,
            yanchor = 'top',
        )

        log.debug('make_layout: margins')
        layout_margins = dict(
            l = 5, r = 5,
            t = 5, b = 5,
            pad = 0,
            autoexpand = True
        )

        log.debug('make_layout: object')
        layout = go.Layout(
            font = dict(size=fontsize),
            plot_bgcolor = bgcolor,
            title = title,
            hidesources = True,
            hovermode = 'y',
            clickmode = 'event+select',
            dragmode = 'pan',
            showlegend = True,
            legend = layout_legend,
            margin = layout_margins,
            xaxis = layout_xaxis,
            yaxis = layout_yaxis,
        )
        log.debug('made layout: %s', str(layout))
    except Exception as e:
        log.error('make_layout NOT made!!')
        raise e
    else:
        return layout


def plot_bar_chart(fp, df):
    """create bar chart from passed dataframe, then save result in fp.parent"""
    try:
        log.info('Creating bar chart for %s', fp.name)

        image_name = fp.stem + '.svg'
        file_name = fp.stem + '.html'
        # log.debug('bar_chart: image: %s, file: %s', image_name, file_name)

        try:
            log.debug('bar_chart: gonna set layout vars')

            colors = [
                'darkcyan', 'chocolate', 'darkmagenta',
                'seagreen', 'lightsteelblue', 'lightcoral',
                'olivedrab', 'darkslateblue', 'plum', 'teal',
            ]
            marker_line = {'color': 'black',
                           'width': 1 }
        except Exception as e:
            log.error('bar_chart: layout variables NOT set')
            raise e

        try:
            log.debug('bar_chart: gonna make layout')
            layout = make_layout()

            log.debug('bar_chart: gonna modify layout specs')
            layout_title = ''.join([
                '<a href="', fp.name, '".csv" class="strong" download>'
                'Project ', parse_project_name(fp.stem), ' Read Counts',
                '</a>'
            ])
            layout['title'] = layout_title

            # height = number of records plus top and bottom margins
            plot_height = df.index.size * 25 \
                          + layout_margins['t'] \
                          + layout_margins['b']
            layout['height'] = plot_height

            layout.xaxis.update(dict(
                # title = 'Number of Reads',
                ticksuffix = ' reads',
                tickangle = -5,
                side = 'top',
            ))

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
            log.debug('bar_chart: layout: %s', str(layout))
        except Exception as e:
            log.error('bar_chart: layout NOT made')
            raise e

        try:
            log.debug('bar_chart: gonna make data')
            data = []
            for i in range(df.columns.size):
                colname = df.columns[i]
                log.debug('bar_chart: column: %s', colname)
                bar = go.Bar(
                    orientation = 'h',
                    name = colname,
                    hoverinfo = "x+name",
                    hoverlabel = {'bgcolor': 'white'},  # TODO: hoverlabel bg?
                    marker = {'color': colors[i],
                              'line': marker_line},
                    x = df[colname],
                    y = df.index,
                    text = df[colname],
                    textposition = 'outside' if i is 1 else 'inside', 
                    textfont = {'size': 14,
                                'color': 'black'},
                    # transforms = [{
                    #     type: 'sort', # or 'filter' -  TODO: transform need 'button' present?
                    #     target: df[colname],
                    #     order: 'descending',
                    #     enabled: True,
                    # }],
                )
                data.append(bar)
            # log.debug('bar_chart: data: %s', str(data))
        except Exception as e:
            log.error('bar_chart: data NOT made')
            raise e

        try:
            log.debug('bar_chart: gonna make figure')
            fig = go.Figure(data=data, layout=layout)
            # log.debug('bar_chart: made figure')
            # log.debug('bar_chart: figure %s', str(fig.__dict__))
        except Exception as e:
            log.error('bar_chart: figure')
            raise e

        try:
            log.debug('bar_chart: gonna make plot')
            plotly_config['modeBarButtonsToRemove'] = ['toggleSpikelines', 'sendDataToCloud', ]

            plot = ply.plot(fig,
                            auto_open = False,
                            image = 'svg',
                            image_height = '100%',
                            output_type = 'div',
                            image_filename = image_name,
                            filename = file_name,
                            config = plotly_config,
                            )
            # log.debug('bar_chart: made bar plot!')
            # log.debug('bar_chart: plots: %s', str(plots))

        except Exception as e:
            log.error('bar_chart: plot not working')
            raise e

    except Exception as e:
        log.error('bar_chart: plotting for file "%s"', fp.name)
        raise e
    else:
       return plot


def plot_16S_read_counts(run_path, flowcell=None, svg_only=False, sort_by='nonhost'):
    """if 16S pipeline's log of number of reads deleted from each step exists,
       then create plots from the csv data within.
       Return the plotly-specific interactive output, or only the svg data.
    """
    log.info('Plotting 16S pipeline QC')
    if not svg_only:
        interactive = True
    # pre-create dict of file paths:
    plot_map = {} # e.g. {'file.name': 'path to plotly output html file or svg image'}
    try:
        # check file(s) exist / find files by glob suffix .csv
        try:
            fpaths = find_pipeline_qc_files(run_path)
            # log.debug('plot_16S: fpaths: %s', str(fpaths))
        except Exception as e:
            log.error('Issues finding files in "%s"', run_path)
            raise e

        try:
            # read contents of each filepath
            # pipe logs have header:
            #       Sample_name,QC_raw,QC_trim,QC_combined,QC_nonchimera,QC_nonhost
            readcnts = ['raw', 'trim', 'combined', 'nonchimera', 'nonhost']
            colnames = ['Sample_Name'] + readcnts
            log.debug('plot_16S: colnames=%s', str(colnames))
            for fp in fpaths:
                df = pd.read_csv(fp, header=0, names=colnames, index_col=0)
                log.debug('plot_16S: df.columns=%s', str(df.columns))
                if sort_by:
                    df.sort_values(by=sort_by, ascending=True, inplace=True)
                try:
                    # create stacked bar plots
                    fp_bar = plot_bar_chart(fp, df)
                except Exception as e:
                    log.error('Issues plotting bar: file "%s" in "%s"', fp.name, run_path)
                else:
                    plot_map[fp.stem] = fp_bar

        except Exception as e:
            log.error('Issues plotting qc files in "%s"', run_path)
            raise e

    except Exception as e:
        log.error('Issues in plot_16S in "%s"', run_path)
        raise e
    finally:
        log.info('Plotted %s ', len(plot_map.keys()))
        return plot_map


if __name__ == '__main__':
    try:
        # run_abspath = Path('/var/www/apps/run_qc_devel/runs/20180611_18-microbe-028_BNYL2_qc')
        # run_abspath = Path('/var/www/html/run_qc_devel/20180611_18-microbe-028_BNYL2_qc')
        # run_abspath = '/var/www/apps/run_qc_devel/runs/20180611_18-microbe-028_BNYL2_qc'
        run_abspath = Path('/var/www/apps/run_qc_devel/runs/20180605_18-microbe-027_BNYKP_qc')
        flowcell = 'BNYL2'
        pipeline_16S_qc_plots = plot_16S_read_counts(run_abspath, flowcell)
        print(f'pipeline_16S_qc_plots: {pipeline_16S_qc_plots!s}')
    except Exception as e:
        # current_app.logger.error('issues plotting bar charts for run: %s', run_path) #TODO: is 'run_path var type 'Path' ??
        log.error('issues plotting bar charts for run: %s', run_path)
        raise e
