<h2 align='center'>
NGS Sequencer Run QC<br/>:microbe: :dna: :mag: :dart: :heavy_check_mark:
</h2>

### Features 

 - Shows list of all uploaded sequencer run "names".
 - Each run shows (downloadable) CSV files from sequencing core group.
 - If one CSV is present, basic details are parsed into JSON file and displayed
      in table at top of page.
 - Modular display of other QC details, IFF they're uploaded to the run's folder.
   - Link to list of FastQC results
   - Analysis of FastQC results
   - Distribution of reads graph image
   - Comparison of sequence assemblies on 'positive control' samples
   - Post-analysis read counts after each step in workflow, e.g. assembly, dechimera, ...

---

### Sequencer Run QC Screenshots

> **List of Run QC pages** <br/>
><img style='vertical-align:middle; position:relative; left:2em;' width="300" 
  src="https://github.com/cometsong/mbiome_seqrun_qc/screenshots/run_qc-run_list.png"><br/>
>
> **Base Page of Sequencer Run** <br/>
><img style='vertical-align:middle; position:relative; left:2em;' width="300" 
  src="https://github.com/cometsong/mbiome_seqrun_qc/screenshots/run_qc-run01.png"><br/>
>
> **Run QC page with Read Distributions** <br/>
><img style='vertical-align:middle; position:relative; left:2em;' width="300" 
  src="https://github.com/cometsong/mbiome_seqrun_qc/screenshots/run_qc-run02-read_dist.png"><br/>
>
> **Run QC page with 16S Read Counts** <br/>
><img style='vertical-align:middle; position:relative; left:2em;' width="300"
  src="https://github.com/cometsong/mbiome_seqrun_qc/screenshots/run_qc-run03-read_counts.png"><br/>
>
> **Run QC page with Control Assembly Comparison** <br/>
><img style='vertical-align:middle; position:relative; left:2em;' width="300" 
  src="https://github.com/cometsong/mbiome_seqrun_qc/screenshots/run_qc-run04-pos-ctrl.png"><br/>

---

## Resources

 - [Issue Tracker](https://github.com/cometsong/mbiome_seqrun_qc/issues)
 - [Code](https://github.com/cometsong/mbiome_seqrun_qc)
