class NodosGraph {
    constructor() {
        this.svg = d3.select('#graph');
        this.container = this.svg.append('g');
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        this.tooltip = null;
        this.selectedNode = null;
        
        this.init();
    }

    init() {
        // Set up SVG dimensions
        const containerRect = document.querySelector('.graph-container').getBoundingClientRect();
        this.width = containerRect.width;
        this.height = containerRect.height;
        
        this.svg
            .attr('width', this.width)
            .attr('height', this.height);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                this.container.attr('transform', event.transform);
            });

        this.svg.call(zoom);

        // Create tooltip
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        // Add event listeners
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzePost();
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    handleResize() {
        const containerRect = document.querySelector('.graph-container').getBoundingClientRect();
        this.width = containerRect.width;
        this.height = containerRect.height;
        
        this.svg
            .attr('width', this.width)
            .attr('height', this.height);

        if (this.simulation) {
            this.simulation
                .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                .alpha(0.3)
                .restart();
        }
    }

    async analyzePost() {
        const postUrl = document.getElementById('postUrl').value;
        const loadingEl = document.getElementById('loading');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        // Show loading state
        loadingEl.style.display = 'block';
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analizando...';

        try {
            const response = await fetch('/nodos/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ post_url: postUrl })
            });

            if (!response.ok) {
                throw new Error('Failed to analyze post');
            }

            const data = await response.json();
            this.renderGraph(data);
            this.updateStats(data.stats);

        } catch (error) {
            console.error('Error:', error);
            alert('Error analyzing post. Please try again.');
        } finally {
            // Hide loading state
            loadingEl.style.display = 'none';
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analizar post';
        }
    }

    renderGraph(data) {
        // Clear previous graph
        this.container.selectAll('*').remove();

        // Prepare data
        this.nodes = [...data.nodes];
        this.links = data.edges.map(d => ({
            source: d.source,
            target: d.target,
            type: d.type
        }));

        // Create force simulation
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(d => d.size + 5));

        // Create links
        const link = this.container.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.links)
            .enter().append('line')
            .attr('class', 'link')
            .style('stroke-width', d => d.type === 'repost' ? 3 : 2)
            .style('stroke-dasharray', d => d.type === 'repost' ? '5,5' : 'none');

        // Create nodes
        const node = this.container.append('g')
            .attr('class', 'nodes')
            .selectAll('circle')
            .data(this.nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => d.size)
            .attr('fill', d => d.color)
            .style('opacity', 0.9)
            .call(this.drag(this.simulation));

        // Add labels
        const labels = this.container.append('g')
            .attr('class', 'labels')
            .selectAll('text')
            .data(this.nodes)
            .enter().append('text')
            .attr('class', 'node-label')
            .text(d => d.label.split('.')[0]) // Show username without domain
            .attr('dy', d => d.size + 15);

        // Add interactions
        this.addNodeInteractions(node);

        // Update positions on simulation tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });
    }

    addNodeInteractions(node) {
        node
            .on('mouseover', (event, d) => {
                this.showTooltip(event, d);
                this.highlightConnections(d);
            })
            .on('mouseout', (event, d) => {
                this.hideTooltip();
                this.unhighlightConnections();
            })
            .on('click', (event, d) => {
                this.selectNode(d);
            });
    }

    showTooltip(event, d) {
        const createdDate = d.created_at ? new Date(d.created_at).toLocaleString() : 'Unknown';
        
        const content = `
            <strong>${d.label}</strong><br/>
            <small>@${d.handle || d.label}</small><br/>
            Type: ${d.type}<br/>
            Created: ${createdDate}<br/>
            <div style="margin: 8px 0; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                ${d.text}
            </div>
            <small>Replies: ${d.metrics.replies} | Reposts: ${d.metrics.reposts} | Likes: ${d.metrics.likes}</small>
        `;

        this.tooltip
            .style('opacity', 1)
            .html(content)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
    }

    hideTooltip() {
        this.tooltip.style('opacity', 0);
    }

    highlightConnections(selectedNode) {
        // Highlight connected nodes and links
        this.container.selectAll('.node')
            .style('opacity', d => {
                return this.isConnected(selectedNode, d) ? 1 : 0.3;
            });

        this.container.selectAll('.link')
            .style('opacity', d => {
                return d.source.id === selectedNode.id || d.target.id === selectedNode.id ? 1 : 0.1;
            });
    }

    unhighlightConnections() {
        this.container.selectAll('.node')
            .style('opacity', 0.9);

        this.container.selectAll('.link')
            .style('opacity', 0.6);
    }

    isConnected(nodeA, nodeB) {
        if (nodeA.id === nodeB.id) return true;
        
        return this.links.some(link => 
            (link.source.id === nodeA.id && link.target.id === nodeB.id) ||
            (link.target.id === nodeA.id && link.source.id === nodeB.id)
        );
    }

    selectNode(node) {
        // Remove previous selection
        this.container.selectAll('.node').classed('selected', false);
        
        // Add selection to current node
        this.container.selectAll('.node')
            .filter(d => d.id === node.id)
            .classed('selected', true);

        this.selectedNode = node;
        this.showNodeDetails(node);
    }

    showNodeDetails(node) {
        const detailsEl = document.getElementById('nodeDetails');
        const contentEl = document.getElementById('nodeContent');
        
        const createdDate = node.created_at ? new Date(node.created_at).toLocaleString() : 'Unknown';
        
        const metricsHtml = `
            <div class="node-details-metrics">
                <span class="metric-item"><strong>Replies:</strong> ${node.metrics.replies}</span>
                <span class="metric-item"><strong>Reposts:</strong> ${node.metrics.reposts}</span>
                <span class="metric-item"><strong>Likes:</strong> ${node.metrics.likes}</span>
            </div>
        `;

        contentEl.innerHTML = `
            <div class="node-details-content">
                <h4 class="node-details-label">${node.label}</h4>
                <p class="node-details-handle">@${node.handle || node.label}</p>
                <p class="node-details-info"><strong>Type:</strong> ${node.type}</p>
                <p class="node-details-info"><strong>Created:</strong> ${createdDate}</p>
                <div class="node-details-text-block">
                    <p class="node-full-text">${node.full_text || node.text}</p>
                </div>
                ${metricsHtml}
            </div>
        `;
        
        detailsEl.style.display = 'block';
    }
    
    updateStats(stats) {
        document.getElementById('totalNodes').textContent = stats.total_nodes;
        document.getElementById('totalReplies').textContent = stats.replies;
        document.getElementById('totalReposts').textContent = stats.reposts;
        document.getElementById('totalInteractions').textContent = stats.total_interactions;
        
        document.getElementById('statsPanel').style.display = 'flex';
    }

    drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }
        
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
        
        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }
}

// Initialize the graph when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new NodosGraph();
});