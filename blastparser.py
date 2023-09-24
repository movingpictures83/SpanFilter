# Copyright (c) 2021 Christian Balbin
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import os
import subprocess
import tempfile
from dataclasses import dataclass, field
#from epitopedia.app import config
from dataclasses_json import dataclass_json
import sqlite3

def condFloat(x):
    try:
        retval = float(x)
        return retval
    except:
        if (x == "\'?\'"):
           return '?'
        else:
           return x


#@dataclass_json
#@dataclass
class HitData:
    def __init__(self, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s):
        self.query_accession = a
        self.subject_accession = b
        self.query_start = c
        self.query_end = d
        self.subject_start = e
        self.subject_end = f
        self.aln_query_seq = g
        self.aln_subject_seq = h
        self.evalue = i
        self.qcovs = j
        self.pident = k
        self.staxid = l
        self.match_ranges = m
        self.cigar = n
        self.match_lengths = o
        self.submatch_seqs = p
        self.acc_seq = q
        self.pdb_seqsolv = r
        self.pdb_seqnums = s


class HitsDataContainer(list):
    def filterbyevalue(self, evalue):
        hit_container = HitsDataContainer()
        for hit in self:
            if float(hit.evalue) <= evalue:
                hit_container.append(hit)
        return hit_container

    def filterbyident(self, pident):
        hit_container = HitsDataContainer()
        for hit in self:
            if float(hit.pident) >= pident:
                hit_container.append(hit)
        return hit_container

    def filterbycover(self, qcovs):
        hit_container = HitsDataContainer()
        for hit in self:
            if float(hit.qcovs) >= qcovs:
                hit_container.append(hit)
        return hit_container

    def filterbymatchlen(self, length):
        hit_container = HitsDataContainer()
        for hit in self:
            if max(hit.match_lengths) >= length:
                hit_container.append(hit)

        return hit_container

    def filterbyacc(self, acc_len, cutoff):
        hit_container = HitsDataContainer()
        for hit in self:
            match_acc_num = 0
            match_num = 0

            for acc, match in zip(hit.acc_seq, hit.cigar):

                if acc == "?":
                    match_num = 0
                    match_acc_num = 0
                    continue
                elif match == "|" and float(acc) >= cutoff:
                    match_acc_num += 1
                    match_num += 1
                elif match == "|":
                    match_num += 1
                elif match == " ":
                    match_num = 0
                    match_acc_num = 0
                    continue
                # if hit.subject_accession == "134680.1":
                # print(match_acc_num, match_num)
                if match_acc_num >= 3 and match_num >= 3:
                    hit_container.append(hit)
                    break
        return hit_container

    def tocsv(self, file_path, SQLITE_DATABASE_DIR):
        #if not os.path.exists(file_path):
        #with open(file_path, "w") as output_handle:

        with open(file_path, "w") as output_handle:
            output_handle.write(
                    f"EPI_SEQ Input Structure\tEPI_SEQ Epitope ID\tEPI_SEQ Input Structure Seq Start Pos\tEPI_SEQ Input Structure Seq Stop Pos\tEPI_SEQ Epitope Start Pos\tEPI_SEQ Epitope End Pos\tEPI_SEQ Aln Input Struc Seq\tEPI_SEQ Aln Epitope Seq\tEPI_SEQ Evalue\tEPI_SEQ Qcov\tEPI_SEQ Pident\tEPI_SEQ Epitope Taxid\tEPI_SEQ Span Ranges\tEPI_SEQ Aln Cigar\tEPI_SEQ Span Lengths\tEPI_SEQ Span Seqs\tPDB_DSSP Input Struc ASA\tmmCIF_SEQ Input Struc Solv Seq\tmmCIF_SEQ Input Struc Res Nums\tIEDB_FILT Epitope Seq\tIEDB_FILT Source Seq Acc\tIEDB_FILT Start Pos\tIEDB_FILT Stop Pos\tIEDB_FILT Source Title\tIEDB_FILT Source Org\n"
            )
            con = sqlite3.connect(SQLITE_DATABASE_DIR)
            cur = con.cursor()
            for hit in self:
                cur.execute(f'SELECT linear_peptide_seq, source_antigen_accession, starting_position, ending_position, name, organism_name FROM IEDB_FILT where epitope_id = {hit.subject_accession}')
                row = cur.fetchone()
                
                output_handle.write(
                    hit.query_accession+"\t"+hit.subject_accession+"\t"+str(hit.query_start)+"\t"+str(hit.query_end)+"\t"+str(hit.subject_start)+"\t"+str(hit.subject_end)+"\t"+hit.aln_query_seq+"\t"+str(hit.aln_subject_seq)+"\t"+hit.evalue+"\t"+hit.qcovs+"\t"+hit.pident+"\t"+str(hit.staxid)+"\t"+str(hit.match_ranges)+"\t"+hit.cigar+"\t"+str(hit.match_lengths)+"\t"+str(hit.submatch_seqs).replace('\"','')+"\t"+str(hit.acc_seq)+"\t"+hit.pdb_seqsolv+"\t"+hit.pdb_seqnums+"\t"+row[0]+"\t"+row[1]+"\t"+row[2]+"\t"+row[3]+"\t"+row[4]+"\t"+row[5]+"\n"
                    )
                #output_handle.write(
                #    f"{hit.query_accession}\t{hit.subject_accession}\t{hit.query_start}\t{hit.query_end}\t{hit.subject_start}\t{hit.subject_end}\t{hit.aln_query_seq}\t{hit.aln_subject_seq}\t{hit.evalue}\t{hit.qcovs}\t{hit.pident}\t{hit.staxid}\t{hit.match_ranges}\t{hit.cigar}\t{hit.match_lengths}\t{hit.submatch_seqs}\t{hit.acc_seq}\t{hit.pdb_seqsolv}\t{hit.pdb_seqnums}\t{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}\t{row[5]}\n"
                #)
            con.close()    


    def fromcsv(self, file_path):
        csvfile = open(file_path, 'r')
        csvfile.readline()
        for line in csvfile:
            line=line.strip()
            contents = line.split('\t')
            contents[14] = contents[14].strip('][').split(',')
            for i in range(len(contents[14])):
               contents[14][i] = int(contents[14][i])
            contents[15] = contents[15].strip('][').split(',')
            contents[16] = contents[16].strip('][').replace(' ','').replace('\"','').split(',')
            for i in range(len(contents[16])):
               contents[16][i] = condFloat(contents[16][i])
            tmplist = contents[12].replace(']','').replace('[','').replace(' ','').split(',')
            pos = 0
            contents[12] = []
            while (pos < len(tmplist)):
               contents[12].append([int(tmplist[pos]), int(tmplist[pos+1])])
               pos += 2
            hit = HitData(contents[0], contents[1], int(contents[2]), int(contents[3]), int(contents[4]), int(contents[5]), contents[6], contents[7], contents[8], contents[9], contents[10], int(contents[11]), contents[12], contents[13], contents[14], contents[15], contents[16], contents[17], contents[18])

            self.append(hit)
        csvfile.close()



class BLASTParser:
    def __init__(
        self,
        query_path,
        input_id,
        database,
        acc_seq=False,
        pdb_seqsolv=False,
        pdb_seqnums=False,
        taxids=False,
        evalue=2000000,
        max_target_seqs=2000000,
    ):
        self.__input_id__ = input_id
        self.__database__ = database
        self.__query_seq__ = query_path
        self.__acc_seq__ = acc_seq
        self.__pdb_seqsolv__ = pdb_seqsolv
        self.__pdb_seqnums__ = pdb_seqnums
        self.__taxids__ = taxids
        self.__evalue__ = str(evalue)
        self.__max_target_seqs__ = str(max_target_seqs)

        if taxids:
            self.__get_species_taxids__()

        self.__run_and_parse_BLAST__()

        if acc_seq:
            self.__add_acc_data__()

        if pdb_seqsolv:
            self.__add_pdb_seqsolv__()

        if pdb_seqnums:
            self.__add_pdb_seqnums__()

    def __get_species_taxids__(self):
        fp = tempfile.NamedTemporaryFile(mode="w", delete=False)
        self.__taxid_fpath__ = fp.name

        if isinstance(self.__taxids__, list):
            for taxid in self.__taxids__:
                subprocess.run(["get_species_taxids.sh", "-t", str(taxid)], stdout=fp)
        else:
            subprocess.run(["get_species_taxids.sh", "-t", str(self.__taxids__)], stdout=fp)

        fp.close()

    def __run_and_parse_BLAST__(self):
        outfmt = "10 sacc qstart qend sstart send qseq sseq evalue qcovs pident staxid"
        # add evalue, query coverage, and ident
        if self.__taxids__:
            result = subprocess.run(
                [
                    "blastp",
                    "-db",
                    self.__database__,
                    "-query",
                    self.__query_seq__,
                    "-negative_taxidlist",
                    self.__taxid_fpath__,
                    "-evalue",
                    self.__evalue__,
                    "-max_target_seqs",
                    self.__max_target_seqs__,
                    # "-gapopen",
                    # "32767",
                    # "-gapextend",
                    # "32767",
                    "-outfmt",
                    outfmt,
                ],
                capture_output=True,
            )
        else:
            result = subprocess.run(
                [
                    "blastp",
                    "-db",
                    self.__database__,
                    "-query",
                    self.__query_seq__,
                    "-evalue",
                    self.__evalue__,
                    "-max_target_seqs",
                    self.__max_target_seqs__,
                    # "-gapopen",
                    # "32767",
                    # "-gapextend",
                    # "32767",
                    "-outfmt",
                    outfmt,
                ],
                capture_output=True,
            )

        self.__hit_container__ = HitsDataContainer()

        for line in result.stdout.decode("utf-8").split("\n")[:-1]:
            line = line.split(",")
            # print(line)

            hit_data = HitData(
                self.__input_id__,
                line[0],
                int(line[1]),
                int(line[2]),
                int(line[3]),
                int(line[4]),
                line[5],
                line[6],
                line[7],
                line[8],
                line[9],
                line[10],
            )

            in_match = False
            qres_pos = hit_data.query_start - 1  # need to check if blast alns ever start with gaps in query seq
            cigar = []

            submatch_seqs = []
            submatch_seq = []

            # list of the match range lists below
            match_ranges = []

            # This list will only hold two values, the start and the end of out match ranges
            match_range = []

            for qres, sres in zip(hit_data.aln_query_seq, hit_data.aln_subject_seq):

                # push previous match range to master list, containg start and end of match if full
                if len(match_range) == 2:
                    match_ranges.append(match_range)
                    submatch_seqs.append("".join(submatch_seq))
                    match_range = []
                    submatch_seq = []

                # if the query residue is not a gap char, increment query position
                if qres != "-":
                    qres_pos += 1

                # if either the query or the subject contain a gap, end the match if in a match, otherwise do not start a new match if by some weird chance both the
                # query and subject residue are gap char. This should never happen but just in case.
                if qres == "-" or sres == "-":
                    cigar.append(" ")
                    if in_match == True:
                        in_match = False
                        if sres == "-":
                            match_range.append(qres_pos - 1)
                        else:
                            match_range.append(qres_pos)
                        match_ranges.append(match_range)
                        submatch_seqs.append("".join(submatch_seq))
                        match_range = []
                        submatch_seq = []
                    continue

                # if the residues match and we are not in a match, inititate a match. If in previosuly was in a match and the residues at current pos dont match
                # end the patch and push to the lists of matches above
                if qres == sres:
                    cigar.append("|")
                    submatch_seq.append(qres)

                    if in_match:
                        continue
                    else:
                        in_match = True
                        match_range.append(qres_pos)
                else:
                    cigar.append(" ")

                    if in_match:
                        in_match = False
                        match_range.append(qres_pos - 1)
                        match_ranges.append(match_range)
                        match_range = []
                        submatch_seqs.append("".join(submatch_seq))
                        submatch_seq = []
                    else:
                        continue
            else:

                if in_match:
                    match_range.append(qres_pos)
                    match_ranges.append(match_range)
                    submatch_seqs.append("".join(submatch_seq))
                    submatch_seq = []

                    match_range = []

            hit_data.match_ranges = match_ranges

            match_lengths = []
            for match in match_ranges:
                start = match[0]
                stop = match[1]
                match_lengths.append(stop - (start - 1))

            hit_data.match_lengths = match_lengths

            hit_data.cigar = cigar
            hit_data.submatch_seqs = submatch_seqs

            self.__hit_container__.append(hit_data)

    def gethits(self):
        return self.__hit_container__

    def __add_acc_data__(self):
        for hit in self.__hit_container__:
            hit.acc_seq = self.__acc_seq__[hit.query_start - 1 : hit.query_end]

    def __add_pdb_seqnums__(self):
        for hit in self.__hit_container__:
            hit.pdb_seqnums = self.__pdb_seqnums__[hit.query_start - 1 : hit.query_end]

    def __add_pdb_seqsolv__(self):
        for hit in self.__hit_container__:
            hit.pdb_seqsolv = self.__pdb_seqsolv__[hit.query_start - 1 : hit.query_end]


if __name__ == "__main__":
    # if using outside of this module
    # from blastparser import BLASTParser

    bp = BLASTParser("path/to/query/seq", "path/to/blast/db")

    # Or to filter blast results using taxids, pass a taxid or a list of taxids to exclude from blast search
    # this requires that you have get_species_taxids.sh in your path and you used a taxid map when creating your db.
    # get_species_taxids.sh is part of blast+
    # For example the call below will exlude all coronaviruses

    # bp = BLASTParser("path/to/query/seq", "path/to/blast/db", taxids=11118)

    # retrieve the parsed hits; this returns an instance of HitsDataContainer which is essentially just a list with
    # some convience methods I wrote for filtering. The hits list contains instances of HitData
    hits = bp.gethits()

    # filters out any hits not containing 5 consecutive matches somewhere in the hit
    hits = hits.filterbymatchlen(5)

    # you can chain filters together
    # hits = hits.filterbymatchlen(5).filterbyident(.60).filterbycover(60)

    # only printing first 3 hits for this example
    for hit in hits[:3]:
        # can access the properties of the HitData for each hit now
        print(f"Subject accession {hit.subject_accession}")
        print(
            " Query Match range(s):",
            "".join([f"{match_range[0]}-{match_range[1]}, " for match_range in hit.match_ranges]),
            "  Match len(s):",
            ", ".join([f"{match_len}" for match_len in hit.match_lengths]),
        )
        print()
        print(f"Query  {hit.query_start:<5d} {hit.aln_query_seq} {hit.query_end:<5d}")
        print(f"            ", "".join(hit.cigar))
        print(f"Subj   {hit.subject_start:<5d} {hit.aln_subject_seq} {hit.subject_end:<5d}")
        print()

        # to handle subbhits (mutliple consecutive hits of >= 5 in a single blast hit)
        # remember hit.matches ranges is a lists of lists as structured as below
        # [[start_pos_int, end_pos_int], [start_pos_int, end_pos_int], ...]
        for index, (start, end) in enumerate(hit.match_ranges):

            # subtract 1 from start to go back to 0 based index (blast uses 1 based index)
            if end - (start - 1) >= 5:
                # only print subhits greater than 5
                print(f"{start} {hit.submatch_seqs[index]} {end}")

        print()
        print()
        print()
        print()
