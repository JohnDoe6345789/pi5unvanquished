# Ngrok Documentation Snapshot
<!-- Offline copy of selected ngrok docs from ngrok/ngrok-docs. -->
_Fetched from https://github.com/ngrok/ngrok-docs on 2025-12-09._

## What is ngrok?
Source: https://github.com/ngrok/ngrok-docs/blob/main/what-is-ngrok.mdx

You can think of ngrok as the front door to your applications.

ngrok is _environment independent_ because it can deliver traffic to services
running anywhere with no changes to your environment's networking. Run your app
on AWS, Azure, Heroku, an on-premise Kubernetes cluster, a Raspberry Pi, and
even your laptop. With ngrok, it all works the same.

ngrok is a _unified ingress platform_ because it combines all the components to
deliver traffic from your services to the internet into one. ngrok
consolidates together your reverse proxy, load balancer, API gateway, firewall,
delivery network, DDoS protection and more.

## What can you do with ngrok?

### Production Ingress

- **API Gateway**: Use ngrok's [Traffic Policy](/traffic-policy/actions/) to secure, protect,
  accelerate and transform traffic to your production APIs.
- **Kubernetes Ingress**: Run the [ngrok Kubernetes Operator](/k8s/) to create ingress
  to Kubernetes services running in any cluster.
- **Identity-Aware Proxy**: Use ngrok's [OAuth](/traffic-policy/actions/oauth/),
  [JWT Validation](/traffic-policy/actions/jwt-validation/), or [OpenID
  Connect](/traffic-policy/actions/oidc/) actions to federate your
  app's authentication to an identity provider.
- **Load Balancer**: Use [Endpoint
  Pools](/universal-gateway/endpoint-pooling/) to load-balance traffic for
  scalability, failover, or to do blue/green and canary deployments.

### Ingress to external networks

- **APIs in customer networks**: Run the lightweight [ngrok agent](/agent/) or
  [Kubernetes Operator](/k8s/) in your customers' environments to securely
  connect to APIs in their networks without complex network configuration.
- **APIs on devices**: Run [ngrok as a service](/agent/#running-ngrok-in-the-background) on
  your devices to create secure URLs for their local APIs enabling your cloud
  service to control and administrate them.
- **APIs in local dev environments**: Import [ngrok as a library](/agent-sdks)
  into your own CLI so you can create better local dev experiences for your
  developer customers.

### Development and testing

- **Webhook Testing**: Run ngrok on your local machine to get a URL to receive
  webhooks directly in the app you're developing. [Inspect and replay
  requests](/agent/web-inspection-interface/) for fast development.
- **Local Previews**: Demo a website running on your local machine to a client
  or stakeholder without deploying to a staging site.
- **Mobile Backend Testing**: Test your mobile apps against a backend that
  you're developing on your local machine.

### Remote access

- **SSH**: Create [TCP endpoints](/universal-gateway/tcp/) to enable SSH access to remote machines.
- **RDP**: Create [TCP endpoints](/universal-gateway/tcp/) to enable RDP access to remote machines.

## How does ngrok work?
Source: https://github.com/ngrok/ngrok-docs/blob/main/how-ngrok-works.mdx

## Overview

ngrok operates a global network of servers called the _ngrok cloud service_ where it
accepts traffic to your upstream services from clients on the internet. The
URLs that it receives traffic on are your _endpoints_. You configure _modules_
that ngrok will use to authenticate, transform and accelerate that traffic as
it is sent to your upstream service.

Unlike traditional reverse proxies, ngrok does not transmit traffic to your
upstream services by forwarding to IP addresses. Instead, you run a small piece
of software alongside your service called an _agent_ which connects to
ngrok's global service via secure, outbound persistent TLS connections. When
traffic is received on your endpoints at ngrok's cloud service, it is transmitted to
the agent via those TLS connections and finally from the agent to your upstream
service.

You can choose how to run the agent software in different form factors. It's
lightweight and easy to install.

1. **As a service:** Run a small side process called the [ngrok agent](/agent/)
   as a background OS service.
1. **As an interactive CLI:** Run the [ngrok agent](/agent/) interactively from
   the command line while developing and testing.
1. **As an SDK embedded in your app:** Include a small [Agent SDK](/agent-sdks) library
   directly into your application software that returns a socket-like object.
1. **As a Kubernetes Controller:** Run the [ngrok Kubernetes Operator](/k8s/) in a
   Kubernetes environment.

## ngrok versus traditional reverse proxies

ngrok doesn't forward to IP addresses like traditional reverse proxies and
instead sends connections to your upstream service via a lightweight piece of
agent software running alongside or in your application.

This unique architecture confers several important benefits over the
traditional model.

First, it means you can run your services _anywhere_—any cloud such as AWS or
Azure, any application platform like Heroku, an on-prem data center, a Raspberry
Pi in your home, or even on your laptop.

Second, it allows ngrok to provide ingress with zero networking configuration.
You don't need to work with arcane networking primitives like DNS, IPs, certificates, or ports. 
That configuration is pushed to ngrok's cloud service and it's all handled automatically for you.

Third, ngrok can protect you from attacks and enforce authentication without
the concern that someone could 'go around' ngrok by discovering your upstream
IP addresses.

## Agent CLI Quickstart
Source: https://github.com/ngrok/ngrok-docs/blob/main/getting-started/index.mdx

ngrok's core functionality is built around [Agent Endpoints](/universal-gateway/agent-endpoints/): endpoints that connect your locally running apps to the internet through the ngrok cloud service and are only available as long as the agent is running somewhere.
Common use cases include granting remote access to IoT devices, enabling your Kubernetes clusters to communicate with each other, and allowing external connections to a local gaming server.

The simplest way to get started is to create an agent endpoint that forwards public traffic to your localhost using the [ngrok Agent CLI](/agent/).
This quickstart walks you through that process, as well as how to implement basic security measures by requiring visitors to log in with a Google account to access your app.

## What you'll need

- An [ngrok account](https://dashboard.ngrok.com/signup).
- Your [ngrok auth token](https://dashboard.ngrok.com/get-started/your-authtoken).

## 1. Install the ngrok Agent CLI

Run the command that corresponds to your operating system to install the Agent CLI:

<Tabs>
<Tab title="Mac OS">

```bash
brew install ngrok
```

</Tab>
<Tab title="Debian Linux">

```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
```

</Tab>
<Tab title="Windows">

Install via the <a href="ms-windows-store://pdp/?ProductId=9mvs1j51gmk6">Windows App Store</a>

</Tab>
</Tabs>

Or [follow the direct installation guide](https://download.ngrok.com?tab=download) if you can't use one of the options above.

To test that it's been installed correctly, run the following command in your terminal and confirm that ngrok prints its help text.

```bash
ngrok help
```

## 2. Connect your account

Connect your agent to your ngrok account by providing your auth token as shown below—replace `$YOUR_TOKEN` with the string given to you [in the dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).

```bash
ngrok config add-authtoken $YOUR_TOKEN
```

## 3. Start your app or service

Start up the app or service you'd like to put online.
This is the app that your agent endpoint will forward online traffic to.

If you don't have an app to work with, you can create a minimal app in your language of choice using the following code to set up a basic HTTP server at port `8080`.

<CodeGroup>

```javascript title="service.js"
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    const html = `
    <html>
    <head><title>Test Page</title></head>
    <body><h1>Hello from Node.js HTTP Server!</h1></body>
    </html>
    `;
    res.end(html);
});

const port = 8080;
server.listen(port, () => {
    console.log(`Serving custom HTML at http://localhost:${port}`);
});
```

```go title="service.go"
package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello from Go HTTP Server!")
}

func main() {
	http.HandleFunc("/", handler)

	fmt.Println("Starting server at http://localhost:8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Server failed:", err)
	}
}
```

```python title="service.py"
from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = b"""
        <html>
        <head><title>Test Page</title></head>
        <body><h1>Hello from Python HTTP Server!</h1></body>
        </html>
        """
        self.wfile.write(html)

def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving custom HTML at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
```

</CodeGroup>

Navigate to the directory where this file is located and start the server.

## 4. Put your app online

Start the ngrok agent by running the following command (replace `8080` if your app is running on a different port).

```bash
ngrok http 8080
```

<Note>
All accounts come with a free dev domain that is automatically chosen when you start an endpoint. You can add the optional `--url` flag to customize this domain on paid plans.
</Note>

The agent should print a console UI to your terminal to confirm that it's online and forwarding as intended.
Open the forwarding URL in your browser to see your web application, which is now available over HTTPS with a valid certificate that ngrok automatically manages for you.

## 5. Secure your app

ngrok makes it simple to add authentication to your app by implementing a [Traffic Policy](/traffic-policy/).
Using the Agent CLI, you can add a traffic policy to your endpoint by editing your ngrok config file, which was automatically created when you provided your auth token in step 3.

Terminate the agent endpoint that you started up in step 5, then run the following command in your terminal to open `ngrok.yml`:

```bash
ngrok config edit
```

You should see a new console UI with your config version and auth token already set.
Below the auth token, paste the following snippet into the editor and then save and exit the config file.
This policy states that whenever an HTTP/S request is made to `$YOUR_DOMAIN`, the agent endpoint should redirect the user to Google OAuth for authentication before proceeding to the app running on port `8080`.

```yaml title="ngrok.yml"
endpoints:
  - name: cli-quickstart
    url: $YOUR_DOMAIN
    traffic_policy:
      on_http_request:
        - actions:
          - type: oauth
            config:
              provider: google
    upstream:
      url: 8080
      protocol: http1
```

<Note>
This example uses ngrok's default Google OAuth application.
To use your own, see [the OAuth Traffic Policy Action documentation](/traffic-policy/actions/oauth/#google-example).
</Note>

Now you can start up your endpoint using its name:

```bash
ngrok start cli-quickstart
```

When you visit your public URL you should be prompted to authenticate by logging in with a Google account before you can access your app.

## What's next?

In this guide, you learned how to create an agent endpoint to forward traffic from the internet to an app running on your local device using the ngrok agent CLI.
You were introduced to some of the most common commands you should know, and you implemented a traffic policy, which can be used for many kinds of actions beyond the basic authentication example here.
You also saw how to edit your config file to make your agent endpoints repeatable and scalable by assigning a name you can refer back to with URLs, protocols, and actions already defined.
What else can you do with these features?

- If you need to interact with ngrok agent endpoints programmatically, use one of the Agent SDKs which are available for [JavaScript (Node.js)](/getting-started/javascript/), [Go](/getting-started/go/), [Python](/getting-started/python/), and [Rust](/getting-started/rust/).
- If your use case calls for a centrally managed, always-on endpoint instead of one that is only available when an agent is running, you should proceed to [getting started with Cloud Endpoints](/getting-started/cloud-endpoints-quickstart/).
- This quickstart barely scratches the surface of what's possible with a traffic policy—check out the [Actions overview](/traffic-policy/actions/) to see what else you can do.
- Visit the [Agent CLI command reference](/agent/cli/) for a complete list of available commands.

## Cloud Endpoints Quickstart
Source: https://github.com/ngrok/ngrok-docs/blob/main/getting-started/cloud-endpoints-quickstart.mdx

Cloud Endpoints provide a persistent way to service traffic.
Unlike Agent Endpoints, which are only available as long as the agent is running, Cloud Endpoints run on ngrok's cloud service, allowing you to accept public traffic even if your internal apps or services are down.

Cloud Endpoints provide an additional layer of traffic management above agent endpoints and can be used to extend their functionality in several key ways.
Using a Traffic Policy, a Cloud Endpoint can route traffic to multiple other endpoints based on criteria such as path, header, IP, and more.

A common use case for this pattern is to create a Cloud Endpoint that accepts public traffic, authenticates it, then routes it to one of several internal agent endpoints running on machines that require privileged access.

This guide walks you through creating Cloud Endpoints in two ways: first, through the ngrok dashboard, and second, using the Agent CLI to interact with the ngrok API.

## What you'll need

- An [ngrok account](https://dashboard.ngrok.com/signup).
- Your [ngrok auth token](https://dashboard.ngrok.com/get-started/your-authtoken).
- An [ngrok API key](https://dashboard.ngrok.com/api-keys).

<Note>
This doc assumes you've already completed the [Agent CLI Quickstart](/getting-started/)—if not, you should start there to learn about some of ngrok's fundamental features before continuing here.
</Note>

## Part one: your first Cloud Endpoint

The best way to familiarize yourself with Cloud Endpoints is to create one in your ngrok dashboard.

### 1. Install the ngrok Agent CLI

If this is your first time using ngrok, run the command that corresponds to your operating system to install the Agent CLI:

<Tabs>
<Tab title="Mac OS">

```bash
brew install ngrok
```

</Tab>
<Tab title="Debian Linux">

```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
```

</Tab>
<Tab title="Windows">

Install via the <a href="ms-windows-store://pdp/?ProductId=9mvs1j51gmk6">Windows App Store</a>

</Tab>
</Tabs>

Or [follow the direct installation guide](https://download.ngrok.com?tab=download) if you can't use one of the options above.

To test that it's been installed correctly, run the following command in your terminal and confirm that ngrok prints its help text.

```bash
ngrok help
```

### 2. Connect your account

Connect your agent to your ngrok account by providing your auth token as shown below—replace `$YOUR_TOKEN` with the string given to you [in the dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).

```bash
ngrok config add-authtoken $YOUR_TOKEN
```

### 3. Create your Cloud Endpoint in the dashboard

[Click here to create a new Cloud Endpoint](https://dashboard.ngrok.com/endpoints/new/cloud) in your dashboard.

There are three bindings to choose from: for this example, select **Public**.
In the **URL** field, enter the domain you reserved in step 1.
Then click **Create Cloud Endpoint**.

This takes you to a page where you can manage your new endpoint's [traffic policy](/traffic-policy/).
You can leave all of the default settings in place for now.

<Info>
Traffic policies are optional for agent endpoints but required for Cloud Endpoints, which is why the dashboard generates one for you automatically.
</Info>

Visit the URL you specified to confirm that it's online.
You should see a default landing page that says "This is your new Cloud Endpoint!"

There are many different things you could do with this endpoint from here.
Now you can put it to work forwarding traffic to an app running on your local device.

### 4. Start your app or service

Start up the app or service you'd like to put online.

If you don't have an app to work with, you can create a minimal app in your language of choice using the following code to set up a basic HTTP server at port `8080`.

<Tabs>
<Tab title="JavaScript">
```javascript
const http = require('http');

const server = http.createServer((req, res) => {
res.writeHead(200, { 'Content-Type': 'text/html' });
const html = `     <html>
    <head><title>Test Page</title></head>
    <body><h1>Hello from Node.js HTTP Server!</h1></body>
    </html>
    `;
res.end(html);
});

const port = 8080;
server.listen(port, () => {
console.log(`Serving custom HTML at http://localhost:${port}`);
});

````

Navigate to the directory where this file is located and run the following command to start the server:

```bash
node service.js
````

</Tab>
<Tab title="Go">

```go title="service.go"
package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello from Go HTTP Server!")
}

func main() {
	http.HandleFunc("/", handler)

	fmt.Println("Starting server at http://localhost:8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Server failed:", err)
	}
}

```

Navigate to the directory where this file is located and run the following command to start the server:

```bash
go run service.go
```

</Tab>
<Tab title="Python">

```python title="service.py"
from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = b"""
        <html>
        <head><title>Test Page</title></head>
        <body><h1>Hello from Python HTTP Server!</h1></body>
        </html>
        """
        self.wfile.write(html)

def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving custom HTML at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
```

Navigate to the directory where this file is located and run the following command to start the server:

```bash
python service.py
```

</Tab>
<Tab title="Rust">

First, create a directory for your Rust project and navigate into it:

```bash
mkdir ngrok-rust-server
cd ngrok-rust-server
```

Next, create a new Rust project:

```bash
cargo init
```

Then, replace the contents of `src/main.rs` with the following code to set up a basic HTTP server:

```rust title="ngrok-rust-server/src/main.rs"
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 512];

    // Read from the stream
    if let Ok(_) = stream.read(&mut buffer) {
        let body = "Hello from Rust HTTP Server!";
        let response = format!(
            "HTTP/1.1 200 OK\r\n\
             Content-Length: {}\r\n\
             Content-Type: text/plain\r\n\
             Connection: close\r\n\r\n\
             {}",
            body.len(),
            body
        );

        if let Err(e) = stream.write_all(response.as_bytes()) {
            eprintln!("Write error: {}", e);
        }

        // Flush to make sure the response is sent
        if let Err(e) = stream.flush() {
            eprintln!("Flush error: {}", e);
        }
    }
}

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080")?;
    println!("Server running at http://127.0.0.1:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => handle_connection(stream),
            Err(e) => eprintln!("Connection failed: {}", e),
        }
    }

    Ok(())
}
```

To run the server, navigate to the root directory of the project (where the `Cargo.toml` file is located) and run the following command:

```bash
cargo run
```

</Tab>
</Tabs>

### 5. Start your Agent endpoint

Start the ngrok agent by running the following command (replace `8080` if your app is running on a different port):

```bash
ngrok http 8080 --url https://default.internal
```

The `--url` flag connects your agent endpoint to your Cloud Endpoint, so when requests are made to your domain they'll be routed here.
The default URL for this is `https://default.internal`, which was defined in the traffic policy when you created the Cloud Endpoint in step 4.

### 6. Test your Cloud Endpoint

Your endpoint should now be online.
Visit your domain URL to see the app that's running on your local device.

## Part two: creating Cloud Endpoints via the ngrok API

Now that you're familiar with the key concepts necessary to work with Cloud Endpoints, you'll create another one using the ngrok API, which you can access via the Agent CLI.
(You can use any HTTP client you prefer for interacting with the ngrok API, but the Agent CLI provides a simple and direct access point for getting started.)

Keep your local app and agent endpoint from part one running.
If you only have one domain to work with, delete the Cloud Endpoint you created in the dashboard before continuing so you can reuse the domain in the steps below.

### 1. Create your traffic policy

Create a `policy.yml` on your local machine and add the code snippet below.
This policy states that incoming HTTP requests should be forwarded to your internal agent endpoint at `https://default.internal`; if that endpoint's not reachable, then it falls back on a custom response to indicate that the app is offline.

```yaml title="policy.yml"
on_http_request:
  - actions:
      - type: "forward-internal"
        config:
          url: "https://default.internal"
         on_error: continue
      - type: custom-response
        config:
          status_code: 200
          headers:
            content-type: text/html
          body: |
             <b>Agent offline!</b>
             <p>Run <code>ngrok http 80 --url https://default.internal</code> to put your application online!</p>

```

### 2. Create your Cloud Endpoint

Create your Cloud Endpoint by running the following command—replace `$YOUR_API_KEY` and `$YOUR_DOMAIN` with their respective values:

```bash
ngrok api endpoints create \
 --api-key $YOUR_API_KEY \
 --description "Cloud endpoint for my API" \
 --type cloud \
 --bindings public \
 --url `$YOUR_DOMAIN` \
 --traffic-policy-file policy.yml
```

This command contains all of the configuration steps you worked through in the dashboard to create a Cloud Endpoint in part one.

### 3. Test your endpoint

Your endpoint should now be online.
Visit your reserved domain URL to see the app that's running on your local device.

To see the fallback response, terminate your local app or agent endpoint and then visit your Cloud Endpoint URL again.
You should see the custom message defined in `policy.yml.`

## What's next?

In this guide, you learned how to create a Cloud Endpoint using both the dashboard and the ngrok API.
You configured a basic traffic policy to forward requests from one endpoint to another, and you saw how Cloud Endpoints can be layered on top of agent endpoints to route traffic to different services and fallback responses based on the criteria you define.
What else can you do with these features?

- See [the Cloud Endpoints overview](/universal-gateway/cloud-endpoints/#use-cases) to learn more about use cases, how they compare to agent endpoints, and more.
- If you need to interact with Cloud Endpoints programmatically, check out ngrok's [API client libraries](/api/#client-libraries).
- See [Load Balancing with Cloud Endpoints](/universal-gateway/cloud-endpoints/forwarding-and-load-balancing/) to learn how to distribute traffic across multiple internal endpoints.
- This quickstart barely scratches the surface of what's possible with a traffic policy—check out the [Actions overview](/traffic-policy/actions/) to see what else you can do.
