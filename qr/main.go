package main

import (
	"encoding/csv"
	"fmt"
	"image"
	_ "image/jpeg"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/makiuchi-d/gozxing"
	"github.com/makiuchi-d/gozxing/qrcode"
	"github.com/pkg/errors"
)

func main() {
	results, err := processDir("../actas")
	if err != nil {
		panic(err)
	}

	csvFile, err := os.Create("resultados_v2.csv")
	if err != nil {
		panic(err)
	}
	defer csvFile.Close()

	writer := csv.NewWriter(csvFile)
	defer writer.Flush()
	headers := []string{"acta", "codigo", "maduro", "edmundo", "martinez", "bertucci", "brito", "ecarri", "fermin", "ceballos", "marquez", "conde_pajuo",  "total_validos", "total_nulo", "total_invalido"}
	writer.Write(headers)
	for _, r := range results {
		totals := r.candidateTotals()
		nmm := totals[candidateMaduro]
		egu := totals[candidateGonzalez]
		lm := totals[candidateMartinez]
		jber := totals[candidateBertucci]
		jb := totals[candidateBrito]
		ae := totals[candidateEcarri]
		cf := totals[candidateFermin]
		dc := totals[candidateCeballos]
		em := totals[candidateMarquez]
		ecp := totals[candidateRausseo]
		writer.Write([]string{
			r.ActaFilename,
			r.ActaCode,
			strconv.Itoa(nmm),
			strconv.Itoa(egu),
			strconv.Itoa(lm),
			strconv.Itoa(jber),
			strconv.Itoa(jb),
			strconv.Itoa(ae),
			strconv.Itoa(cf),
			strconv.Itoa(dc),
			strconv.Itoa(em),
			strconv.Itoa(ecp),
			strconv.Itoa(r.ValidVotes),
			strconv.Itoa(r.NullVotes),
			strconv.Itoa(r.InvalidVotes),
		})
	}

	log.Printf("DONE :)")
}

func processDir(dir string) ([]*Result, error) {
	files, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}

	results := []*Result{}
	for _, file := range files {
		if !file.IsDir() {
			log.Printf("processing %s...", file.Name())
			result, err := processQR(file.Name(), filepath.Join(dir, file.Name()))
			if err != nil {
				log.Printf("failed to process %s: %s", file.Name(), err)
				continue
			}
			byCandidate := result.candidateTotals()
			log.Printf("successfully processed %s... maduro %d, edmundo %d", file.Name(), byCandidate[candidateMaduro], byCandidate[candidateGonzalez])
			results = append(results, result)
		}
	}

	return results, nil
}

// types
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

// methods to process QR data
func processQR(filename, path string) (*Result, error) {
	data, err := readQR(path)
	if err != nil {
		return nil, errors.Wrap(err, "failed to read qr code from image")
	}

	return parseQRData(filename, data)
}

func readQR(path string) (string, error) {
	// This function reads the actas QR and retuns a string with the actas data
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

func parseQRData(filename, data string) (*Result, error) {
	// This function parses the data from the actas QR
	// The QR code from the actas outputs a string with this format:
	// 110601011.04.1.0001!122,1,0,0,4,2,0,0,2,1,0,1,2,1,0,0,0,5,0,2,0,0,0,0,0,0,0,0,1,0,0,0,0,8,22,406,0,1!0!0
	// it has 4 parts, divided by an exclamation symbol "!"
	// the first part corresponds to the voting center code: 110601011.04.1.0001
	// the second part has the votes per party, following the order in ballotOrder: 122,1,0,0,4,2,0,0,2,1,0,1,2,1,0,0,0,5,0,2,0,0,0,0,0,0,0,0,1,0,0,0,0,8,22,406,0,1
	// the third part is the null votes
	// the fourth part is the invalid votes
	parts := strings.Split(data, "!")
	if len(parts) != 4 {
		return nil, errors.New(fmt.Sprintf("did not find 4 parts in data: %s", data))
	}

	actaCode := parts[0]
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
