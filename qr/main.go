package main

import (
	"encoding/csv"
	"fmt"
	"image"
	_ "image/jpeg"
	"log"
	"os"
	"path/filepath"
	"slices"
	"strconv"
	"strings"

	"github.com/makiuchi-d/gozxing"
	"github.com/makiuchi-d/gozxing/qrcode"
	"github.com/pkg/errors"
)

var resultsFile = "resultados.csv"

func main() {
	filenames, err := processed(resultsFile)
	if err != nil {
		log.Printf("failed to read results from %s", resultsFile)
		panic(err)
	}

	results, err := processDir(filenames, "../actas", resultsFile)
	if err != nil {
		panic(err)
	}

	log.Printf("processed %d new actas", len(results))
	log.Printf("DONE :)")
}

func processed(path string) ([]string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}

	r := csv.NewReader(f)
	records, err := r.ReadAll()
	if err != nil {
		return nil, err
	}

	filenames := []string{}
	for i, row := range records {
		if i == 0 { // skip header
			continue
		}
		filenames = append(filenames, row[0])
	}
	log.Printf("read %d existing processed actas", len(filenames))

	return filenames, nil
}

func appendResults(results []*Result, path string) error {
	// We append so we avoid clobbering existing data, and punt on parsing existing csv data
	csvFile, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		panic(err)
	}
	defer csvFile.Close()

	writer := csv.NewWriter(csvFile)
	for _, r := range results {
		err = writer.Write(r.asRow())
		if err != nil {
			return err
		}
	}
	writer.Flush()
	log.Printf("flushed %d rows", len(results))

	return nil
}

func processDir(processed []string, dir string, resultsFile string) ([]*Result, error) {
	files, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}

	results := []*Result{}
	unflushed := []*Result{}
	for _, file := range files {
		if len(unflushed) > 0 && len(unflushed)%100 == 0 { // flush every 100 results
			err = appendResults(unflushed, resultsFile)
			if err != nil {
				return nil, err
			}
			unflushed = []*Result{}
		}

		if !file.IsDir() {
			filename := file.Name()
			if slices.Contains(processed, filename) {
				log.Printf("skipping %s, already extracted", filename)
				continue
			}
			log.Printf("processing %s...", filename)
			result, err := process(filename, filepath.Join(dir, filename))
			if err != nil {
				log.Printf("failed to process %s: %s", filename, err)
				continue
			}
			byCandidate := result.candidateTotals()
			log.Printf("successfully processed %s... maduro %d, edmundo %d", filename, byCandidate[candidateMaduro], byCandidate[candidateGonzalez])

			results = append(results, result)
			unflushed = append(unflushed, result)
		}
	}
	err = appendResults(unflushed, resultsFile)
	if err != nil {
		return nil, err
	}

	return results, nil
}

type Option struct {
	Candidate string // TODO: make these enums
	Party     string
}

const candidateMaduro = "Maduro Mamaguevo"
const candidateMartinez = "Luis Martinez"
const candidateBertucci = "Javier Bertucci"
const candidateBrito = "Jose Brito"
const candidateEcarri = "Antonio Ecarri"
const candidateFermin = "Claudio Fermin"
const candidateCeballos = "Daniel Ceballos"
const candidateGonzalez = "Edmundo Gonzalez"
const candidateMarquez = "Enrique Marquez"
const candidateRausseo = "El Conde Pajuo"

var ballotOrder = []Option{
	{Candidate: candidateMaduro, Party: "PSUV"},
	{Candidate: candidateMaduro, Party: "PCV"},
	{Candidate: candidateMaduro, Party: "TUPAMARO"},
	{Candidate: candidateMaduro, Party: "PPT"},
	{Candidate: candidateMaduro, Party: "MSV"},
	{Candidate: candidateMaduro, Party: "PODEMOS"},
	{Candidate: candidateMaduro, Party: "MEP"},
	{Candidate: candidateMaduro, Party: "APC"},
	{Candidate: candidateMaduro, Party: "ORA"},
	{Candidate: candidateMaduro, Party: "UPV"},
	{Candidate: candidateMaduro, Party: "EV"},
	{Candidate: candidateMaduro, Party: "PVV"},
	{Candidate: candidateMaduro, Party: "PFV"},
	{Candidate: candidateMartinez, Party: "AD"},
	{Candidate: candidateMartinez, Party: "COPEI"},
	{Candidate: candidateMartinez, Party: "MR"},
	{Candidate: candidateMartinez, Party: "BR"},
	{Candidate: candidateMartinez, Party: "DDP"},
	{Candidate: candidateMartinez, Party: "UNE"},
	{Candidate: candidateBertucci, Party: "EL CAMBIO"},
	{Candidate: candidateBrito, Party: "PV"},
	{Candidate: candidateBrito, Party: "VU"},
	{Candidate: candidateBrito, Party: "UVV"},
	{Candidate: candidateBrito, Party: "MPJ"},
	{Candidate: candidateEcarri, Party: "AP"},
	{Candidate: candidateEcarri, Party: "MOVEV"},
	{Candidate: candidateEcarri, Party: "CMC"},
	{Candidate: candidateEcarri, Party: "FV"},
	{Candidate: candidateEcarri, Party: "ALIANZA DEL LAPIZ"},
	{Candidate: candidateEcarri, Party: "MIN UNIDAD"},
	{Candidate: candidateFermin, Party: "SPV"},
	{Candidate: candidateCeballos, Party: "VPA"},
	{Candidate: candidateCeballos, Party: "AREPA"},
	{Candidate: candidateGonzalez, Party: "UNTC"},
	{Candidate: candidateGonzalez, Party: "MPV"},
	{Candidate: candidateGonzalez, Party: "MUD"},
	{Candidate: candidateMarquez, Party: "CENTRADOS"},
	{Candidate: candidateRausseo, Party: "CONDE"},
}

type Result struct {
	ActaCode     string
	ActaFilename string

	ValidVotes   int
	NullVotes    int
	InvalidVotes int

	Votes map[Option]int
}

func (r *Result) candidateTotals() map[string]int {
	tallies := map[string]int{}
	for opt, v := range r.Votes {
		tallies[opt.Candidate] += v
	}
	return tallies
}

func (r *Result) header() []string {
	return []string{"acta", "codigo", "maduro", "edmundo", "otros", "total_validos", "total_nulo", "total_invalido"}
}

func (r *Result) asRow() []string {
	// For now write just a summary, but we should write all the data so we can dump into a DB.
	totals := r.candidateTotals()
	nmm := totals[candidateMaduro]
	egu := totals[candidateGonzalez]
	return []string{
		r.ActaFilename,
		r.ActaCode,
		strconv.Itoa(nmm),
		strconv.Itoa(egu),
		strconv.Itoa(r.ValidVotes - nmm - egu),
		strconv.Itoa(r.ValidVotes),
		strconv.Itoa(r.NullVotes),
		strconv.Itoa(r.InvalidVotes),
	}
}

func process(filename, path string) (*Result, error) {
	data, err := readQR(path)
	if err != nil {
		return nil, errors.Wrap(err, "failed to read qr code from image")
	}

	return parse(filename, data)
}

func readQR(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	img, _, err := image.Decode(file)
	if err != nil {
		return "", err
	}

	// prepare BinaryBitmap
	bmp, err := gozxing.NewBinaryBitmapFromImage(img)
	if err != nil {
		return "", err
	}

	// decode image
	qrReader := qrcode.NewQRCodeReader()
	result, err := qrReader.Decode(bmp, nil)
	if err != nil {
		return "", err
	}

	return result.String(), nil
}

func parse(filename, data string) (*Result, error) {
	// Example data:
	// 110601011.04.1.0001!122,1,0,0,4,2,0,0,2,1,0,1,2,1,0,0,0,5,0,2,0,0,0,0,0,0,0,0,1,0,0,0,0,8,22,406,0,1!0!0
	parts := strings.Split(data, "!")
	if len(parts) != 4 {
		return nil, errors.New(fmt.Sprintf("did not find 4 parts in data: %s", data))
	}

	actaCode := parts[0] // 110601011.04.1.0001 (first part is the voting center code)
	validVotes := parts[1]
	nullVotes, err := strconv.Atoi(parts[2])
	if err != nil {
		return nil, errors.Wrap(err, "failed to parse null votes")
	}
	invalidVotes, err := strconv.Atoi(parts[3])
	if err != nil {
		return nil, errors.Wrap(err, "failed to parse invalid votes")
	}

	votes := strings.Split(validVotes, ",")
	if len(votes) != 38 {
		return nil, errors.New(fmt.Sprintf("found unexpected number of votes in data: %s", data))
	}

	result := &Result{
		ActaCode:     actaCode,
		ActaFilename: filename,
		NullVotes:    nullVotes,
		InvalidVotes: invalidVotes,
		Votes:        map[Option]int{},
	}
	sum := 0
	for i, v := range votes {
		vInt, err := strconv.Atoi(v)
		if err != nil {
			return nil, errors.Wrap(err, "failed to parse vote")
		}
		opt := ballotOrder[i]
		result.Votes[opt] = vInt
		sum += vInt
	}
	result.ValidVotes = sum

	return result, nil
}
