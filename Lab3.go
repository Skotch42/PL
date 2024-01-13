package main

import (
	"fmt"
	"sync"
)

type Token struct {
	data      string
	recipient int
	ttl       int
}

type Node struct {
	id        int
	left      chan Token
	right     chan Token
	stopped   chan struct{}
	waitGroup *sync.WaitGroup
}

func NewNode(id int, left, right chan Token) *Node {
	return &Node{
		id:        id,
		left:      left,
		right:     right,
		stopped:   make(chan struct{}),
		waitGroup: &sync.WaitGroup{},
	}
}

func (n *Node) Start() {
	n.waitGroup.Add(1)
	go func() {
		defer n.waitGroup.Done()
		for {
			select {
			case t := <-n.left:
				if t.recipient == n.id {
					fmt.Printf("The message '%s' has been successfully delivered to node '%d' (ttl=%d)\n", t.data, n.id, t.ttl)
					close(n.left)
					return
				}

				if t.ttl <= 0 {
					fmt.Printf("The message has expired (ttl=%d)\n", t.ttl)
					close(n.left)
					return
				}

				fmt.Printf("Node %d received token '%s' (ttl=%d)\n", n.id, t.data, t.ttl)
				n.right <- Token{t.data, t.recipient, t.ttl - 1}
				fmt.Printf("Node %d sent token '%s' (ttl=%d)\n\n", n.id, t.data, t.ttl-1)
			case <-n.stopped:
				return
			}
		}
	}()
}

func (n *Node) Stop() {
	close(n.stopped)
	n.waitGroup.Wait()
}

func main() {

	var n int
	fmt.Print("Enter number of nodes: ")
	fmt.Scan(&n)

	nodes := make([]*Node, n)

	channels := make([]chan Token, n)
	for i := range channels {
		channels[i] = make(chan Token)
	}

	for i := 0; i < n; i++ {
		nodes[i] = NewNode(i, channels[i], channels[(i+1)%n])
	}

	for i := 0; i < n; i++ {
		go nodes[i].Start()
	}

	var msg string
	fmt.Print("Enter message: ")
	fmt.Scan(&msg)

	var recipient int
	fmt.Print("Enter recipient: ")
	fmt.Scan(&recipient)

	var ttl int
	fmt.Print("Enter ttl: ")
	fmt.Scan(&ttl)
	fmt.Print("\n")

	channels[0] <- Token{msg, recipient, ttl}
	fmt.Printf("Main thread sent token '%s' to node %d (ttl=%d)\n\n", msg, 0, ttl)

	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < n; i++ {
			nodes[i].Stop()
		}
	}()

	wg.Wait()
}
