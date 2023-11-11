package main

import (
	"fmt"
	"os"
	"os/exec"
)

func main() {
	script_path := os.Args[1]
	dataset_path := os.Args[2]

	cmd := exec.Command(
		"python3.11",
		script_path,
		"-d "+dataset_path,
	)

	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println("Python Error:")
		fmt.Println(string(output))
		fmt.Println(err)
		return
	}

	fmt.Println(string(output))
}
