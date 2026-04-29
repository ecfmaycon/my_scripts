// ==UserScript==
// @name         Painel Prompts
// @namespace    http://tampermonkey.net/
// @version      3.1
// @description  Painel multifuncional de prompts com visual escuro, gradiente, Auto-Enter, gerador SEO, interface móvel e imagens fixas em 1200x1200.
// @author       maycon
// @match        https://gemini.google.com/*
// @match        https://chatgpt.com/* 
// @icon         https://www.google.com/s2/favicons?sz=64&domain=google.com
// @updateURL    https://github.com/ecfmaycon/my_scripts/raw/refs/heads/main/painel.user.js
// @downloadURL  https://github.com/ecfmaycon/my_scripts/raw/refs/heads/main/painel.user.js
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    function criarElemento(tag, estilos = '', texto = '', atributos = {}) {
        const el = document.createElement(tag);
        if (estilos) el.style.cssText = estilos;
        if (texto) el.innerText = texto;
        for (const [chave, valor] of Object.entries(atributos)) {
            el.setAttribute(chave, valor);
        }
        return el;
    }

    function montarPainelFixo() {
        if (document.getElementById('gp-painel-fixo')) return;

        // --- Container Principal ---
        const container = criarElemento('div',
            'position:fixed; top:80px; right:20px; width:340px; background:rgba(15, 15, 20, 0.96); border:1px solid #2a2a36; border-radius:12px; padding:20px; z-index:999999; box-shadow:0 10px 25px rgba(0, 0, 0, 0.7); font-family:"Segoe UI", "Helvetica Neue", sans-serif; color:#fff; backdrop-filter: blur(10px); transition: width 0.3s, opacity 0.3s;',
            '', {id: 'gp-painel-fixo'}
        );
        document.body.appendChild(container);

        // --- Header (Alça para arrastar) ---
        const header = criarElemento('div', 'display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; cursor:move; user-select:none;');
        const headerText = criarElemento('h3', 'margin:0; font-size:16px; font-weight:700; color:#fff; letter-spacing: 1px; pointer-events:none;', '⚡ PAINEL PROMPTS');
        header.appendChild(headerText);
        const btnMinimizar = criarElemento('button', 'background:none; border:none; color:#ddd; cursor:pointer; font-weight:bold; font-size:16px;', '—');
        header.appendChild(btnMinimizar);
        container.appendChild(header);

        // --- LÓGICA DE ARRASTAR (DRAG & DROP) ---
        let isDragging = false;
        let offsetX, offsetY;

        header.addEventListener('mousedown', (e) => {
            if (e.target === btnMinimizar) return;
            isDragging = true;
            const rect = container.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            container.style.right = 'auto';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
            container.style.left = `${e.clientX - offsetX}px`;
            container.style.top = `${e.clientY - offsetY}px`;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // --- Barra de Gradiente ---
        const barraGradiente = criarElemento('div',
            'height:4px; background:linear-gradient(to right, #1a1060, #80216b, #e0594f, #f6c554); margin-bottom:15px; border-radius:2px;'
        );
        container.appendChild(barraGradiente);

        // --- Corpo do Painel ---
        const corpo = criarElemento('div');
        container.appendChild(corpo);

        // --- SISTEMA DE ABAS ---
        const grupoAbas = criarElemento('div', 'display:flex; margin-bottom:15px; border-bottom:1px solid #333344;');
        const abaImagem = criarElemento('button', 'flex:1; padding:8px; background:none; border:none; color:#fff; cursor:pointer; font-weight:bold; font-size:13px; border-bottom:2px solid #e0594f; transition:all 0.2s;', '🖼️ Imagens');
        const abaSEO = criarElemento('button', 'flex:1; padding:8px; background:none; border:none; color:#777; cursor:pointer; font-weight:bold; font-size:13px; border-bottom:2px solid transparent; transition:all 0.2s;', '🔍 SEO');

        grupoAbas.appendChild(abaImagem);
        grupoAbas.appendChild(abaSEO);
        corpo.appendChild(grupoAbas);

        // --- CONTAINERS DAS ABAS ---
        const conteudoImagem = criarElemento('div', 'display:block;');
        const conteudoSEO = criarElemento('div', 'display:none;');
        corpo.appendChild(conteudoImagem);
        corpo.appendChild(conteudoSEO);

        // ==========================================
        // CONTEÚDO: ABA IMAGEM
        // ==========================================
        const grupoProduto = criarElemento('div');
        grupoProduto.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Nome do produto:'));
        const inputProduto = criarElemento('input', 'width:100%; padding:9px; margin-bottom:12px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; font-size:13px; outline:none;', '', {placeholder: 'Ex: Fone Bluetooth...'});
        grupoProduto.appendChild(inputProduto);
        conteudoImagem.appendChild(grupoProduto);

        const grupoQuantidade = criarElemento('div', 'display:none;');
        grupoQuantidade.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Quantidade no KIT:'));
        const inputQuantidade = criarElemento('input', 'width:100%; padding:9px; margin-bottom:12px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; font-size:13px; outline:none;', '', {type: 'number', min: '2', max: '20', value: '2'});
        grupoQuantidade.appendChild(inputQuantidade);
        conteudoImagem.appendChild(grupoQuantidade);

        const grupoSpecs = criarElemento('div', 'display:none;');
        grupoSpecs.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Especificações / Medidas:'));
        const inputSpecs = criarElemento('textarea', 'width:100%; padding:9px; margin-bottom:12px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; resize:none; font-size:13px; outline:none;', '', {rows: '3', placeholder: 'Detalhes...'});
        grupoSpecs.appendChild(inputSpecs);
        conteudoImagem.appendChild(grupoSpecs);

        conteudoImagem.appendChild(criarElemento('label', 'display:block; margin-bottom:10px; font-size:13px; font-weight:600; color:#ddd;', 'Estilo da imagem:'));
        const grupoRadiosImagem = criarElemento('div', 'margin-bottom:15px; font-size:12px; line-height:1.6; color:#ccc;');

        const radiosImagem = [];
        const opcoesImagem = [
            {val: '1', texto: ' Produto ambientado'},
            {val: '2', texto: ' Pessoa utilizando o produto'},
            {val: '3', texto: ' Benefícios c/ especificações'},
            {val: '4', texto: ' Gráfico Comparação'},
            {val: '5', texto: ' Imagem de KIT ambientado'},
            {val: '6', texto: ' Design c/ Ícones'},
            {val: '7', texto: ' Layout Curvo c/ Detalhe e Ícones'},
            {val: '8', texto: ' Medidas do Produto'} 
        ];

        opcoesImagem.forEach((op, index) => {
            const label = criarElemento('label', 'display:block; margin-bottom:8px; cursor:pointer;');
            const radio = criarElemento('input', 'margin-right:8px; vertical-align:middle;', '', {type: 'radio', name: 'gptipo', value: op.val});
            if(index === 0) radio.checked = true;
            radiosImagem.push(radio);
            label.appendChild(radio);
            label.appendChild(document.createTextNode(op.texto));
            grupoRadiosImagem.appendChild(label);
        });
        conteudoImagem.appendChild(grupoRadiosImagem);

        // ==========================================
        // CONTEÚDO: ABA SEO
        // ==========================================
        conteudoSEO.appendChild(criarElemento('label', 'display:block; margin-bottom:10px; font-size:13px; font-weight:600; color:#ddd;', 'Modo de Criação SEO:'));
        const grupoRadiosSEO = criarElemento('div', 'display:flex; flex-wrap: wrap; gap:10px; margin-bottom:18px; font-size:12px; color:#ccc;');

        const labelRadioTitulo = criarElemento('label', 'cursor:pointer; display:flex; align-items:center;');
        const radioTituloSEO = criarElemento('input', 'margin-right:5px;', '', {type: 'radio', name: 'seomodo', value: 'titulo', checked: true});
        labelRadioTitulo.appendChild(radioTituloSEO);
        labelRadioTitulo.appendChild(document.createTextNode('Título'));

        const labelRadioDesc = criarElemento('label', 'cursor:pointer; display:flex; align-items:center;');
        const radioDescSEO = criarElemento('input', 'margin-right:5px;', '', {type: 'radio', name: 'seomodo', value: 'descricao'});
        labelRadioDesc.appendChild(radioDescSEO);
        labelRadioDesc.appendChild(document.createTextNode('Descrição'));

        // NOVA OPÇÃO: ANÚNCIO COMPLETO
        const labelRadioAnuncio = criarElemento('label', 'cursor:pointer; display:flex; align-items:center;');
        const radioAnuncioSEO = criarElemento('input', 'margin-right:5px;', '', {type: 'radio', name: 'seomodo', value: 'anuncio'});
        labelRadioAnuncio.appendChild(radioAnuncioSEO);
        labelRadioAnuncio.appendChild(document.createTextNode('Anúncio Completo'));

        grupoRadiosSEO.appendChild(labelRadioTitulo);
        grupoRadiosSEO.appendChild(labelRadioDesc);
        grupoRadiosSEO.appendChild(labelRadioAnuncio);
        conteudoSEO.appendChild(grupoRadiosSEO);

        // --- CAMPOS PARA TÍTULO E DESCRIÇÃO (ANTIGOS) ---
        const grupoProdutoSEO = criarElemento('div');
        const labelProdutoSEO = criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Nome do Produto:');
        const inputProdutoSEO = criarElemento('input', 'width:100%; padding:9px; margin-bottom:12px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; font-size:13px; outline:none;', '', {placeholder: 'Ex: Fone Sem Fio'});
        grupoProdutoSEO.appendChild(labelProdutoSEO);
        grupoProdutoSEO.appendChild(inputProdutoSEO);
        conteudoSEO.appendChild(grupoProdutoSEO);

        const grupoLojaSEO = criarElemento('div', 'display:none;');
        grupoLojaSEO.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Nome da Loja:'));
        const inputLojaSEO = criarElemento('input', 'width:100%; padding:9px; margin-bottom:12px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; font-size:13px; outline:none;', '', {placeholder: 'Ex: Loja AvantPro'});
        grupoLojaSEO.appendChild(inputLojaSEO);
        conteudoSEO.appendChild(grupoLojaSEO);

        const grupoSpecsSEO = criarElemento('div');
        grupoSpecsSEO.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Especificações Técnicas:'));
        const inputSpecsSEO = criarElemento('textarea', 'width:100%; padding:9px; margin-bottom:12px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; resize:none; font-size:13px; outline:none;', '', {rows: '3', placeholder: 'Ex: Cor Preta, 110v...'});
        grupoSpecsSEO.appendChild(inputSpecsSEO);
        conteudoSEO.appendChild(grupoSpecsSEO);

        const grupoKeywordsSEO = criarElemento('div');
        grupoKeywordsSEO.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Keywords AvantPro:'));
        const inputKeywordsSEO = criarElemento('textarea', 'width:100%; padding:9px; margin-bottom:15px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; resize:none; font-size:13px; outline:none;', '', {rows: '3', placeholder: 'Cole as keywords aqui...'});
        grupoKeywordsSEO.appendChild(inputKeywordsSEO);
        conteudoSEO.appendChild(grupoKeywordsSEO);

        // --- CAMPO ÚNICO PARA "ANÚNCIO COMPLETO" (NOVO) ---
        const grupoAnuncioCompletoSEO = criarElemento('div', 'display:none;');
        grupoAnuncioCompletoSEO.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:600; color:#ddd;', 'Nome e Descrição do Produto:'));
        const inputAnuncioCompletoSEO = criarElemento('textarea', 'width:100%; padding:9px; margin-bottom:15px; background:#1c1c24; border:1px solid #333344; color:#fff; border-radius:6px; box-sizing:border-box; resize:none; font-size:13px; outline:none;', '', {rows: '7', placeholder: 'Cole aqui o nome, a descrição, e especificações gerais do produto...'});
        grupoAnuncioCompletoSEO.appendChild(inputAnuncioCompletoSEO);
        conteudoSEO.appendChild(grupoAnuncioCompletoSEO);


        // --- BOTÃO DE AÇÃO GLOBAL ---
        const btnGerar = criarElemento('button',
            'width:100%; padding:11px; background:linear-gradient(to right, #1a1060, #80216b, #e0594f, #f6c554); color:white; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:14px; box-shadow:0 3px 6px rgba(0,0,0,0.3); transition: all 0.2s;',
            'Gerar e Enviar para Gemini 🚀'
        );
        corpo.appendChild(btnGerar);

        // --- LÓGICA DE EVENTOS (ABAS E MINIMIZAR) ---
        let modoAtual = 'imagem';

        abaImagem.addEventListener('click', () => {
            modoAtual = 'imagem';
            conteudoImagem.style.display = 'block';
            conteudoSEO.style.display = 'none';
            abaImagem.style.color = '#fff';
            abaImagem.style.borderBottom = '2px solid #e0594f';
            abaSEO.style.color = '#777';
            abaSEO.style.borderBottom = '2px solid transparent';
        });

        abaSEO.addEventListener('click', () => {
            modoAtual = 'seo';
            conteudoImagem.style.display = 'none';
            conteudoSEO.style.display = 'block';
            abaSEO.style.color = '#fff';
            abaSEO.style.borderBottom = '2px solid #e0594f';
            abaImagem.style.color = '#777';
            abaImagem.style.borderBottom = '2px solid transparent';
        });

        // Alternador de Abas Internas de SEO
        [radioTituloSEO, radioDescSEO, radioAnuncioSEO].forEach(radio => {
            radio.addEventListener('change', (e) => {
                const val = e.target.value;
                if (val === 'titulo') {
                    grupoProdutoSEO.style.display = 'block';
                    grupoSpecsSEO.style.display = 'block';
                    grupoKeywordsSEO.style.display = 'block';
                    grupoLojaSEO.style.display = 'none';
                    grupoAnuncioCompletoSEO.style.display = 'none';
                } else if (val === 'descricao') {
                    grupoProdutoSEO.style.display = 'block';
                    grupoSpecsSEO.style.display = 'block';
                    grupoKeywordsSEO.style.display = 'none';
                    grupoLojaSEO.style.display = 'block';
                    grupoAnuncioCompletoSEO.style.display = 'none';
                } else if (val === 'anuncio') {
                    grupoProdutoSEO.style.display = 'none';
                    grupoSpecsSEO.style.display = 'none';
                    grupoKeywordsSEO.style.display = 'none';
                    grupoLojaSEO.style.display = 'none';
                    grupoAnuncioCompletoSEO.style.display = 'block';
                }
            });
        });

        let minimizado = false;
        btnMinimizar.addEventListener('click', () => {
            minimizado = !minimizado;
            corpo.style.display = minimizado ? 'none' : 'block';
            barraGradiente.style.marginBottom = minimizado ? '0' : '15px';
            btnMinimizar.innerText = minimizado ? '▼' : '—';
            container.style.width = minimizado ? '160px' : '340px';
        });

        radiosImagem.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const val = e.target.value;
                grupoProduto.style.display = (['1', '2', '4', '5', '6', '7', '8'].includes(val)) ? 'block' : 'none';
                grupoSpecs.style.display = (['3', '4', '6', '7', '8'].includes(val)) ? 'block' : 'none';
                grupoQuantidade.style.display = (val === '5') ? 'block' : 'none';
            });
        });

        btnGerar.addEventListener('mouseover', () => {
            btnGerar.style.background = 'linear-gradient(to right, #241A87, #A82C84, #EB7266, #F7D27A)';
            btnGerar.style.boxShadow = '0 4px 8px rgba(0,0,0,0.4)';
        });
        btnGerar.addEventListener('mouseout', () => {
            btnGerar.style.background = 'linear-gradient(to right, #1a1060, #80216b, #e0594f, #f6c554)';
            btnGerar.style.boxShadow = '0 3px 6px rgba(0,0,0,0.3)';
        });

        // --- GERAÇÃO E ENVIO ---
        btnGerar.addEventListener('click', () => {
            let promptText = "";

            if (modoAtual === 'imagem') {
                const produto = inputProduto.value.trim();
                const specs = inputSpecs.value.trim();
                let quantidade = parseInt(inputQuantidade.value);
                const tipo = radiosImagem.find(r => r.checked).value;

                if ((['1', '2', '5', '6', '7', '8'].includes(tipo)) && !produto) return alert("⚠️ Digite o nome do produto.");
                if (tipo === '3' && !specs) return alert("⚠️ Digite as especificações.");
                if (['4', '6', '7', '8'].includes(tipo) && (!produto || !specs)) return alert("⚠️ Preencha Produto e Especificações.");

                if (tipo === '5' && (isNaN(quantidade) || quantidade < 2)) {
                    quantidade = 2;
                    inputQuantidade.value = 2;
                }

                if (tipo === '1') {
                    promptText = `Gere 1 única imagem realista de alta qualidade para uso em anúncio de e-commerce (Mercado Livre). O foco principal deve ser ${produto}, mantendo 100% fidelidade ao design original do produto, sem alterações de cor, formato, proporção ou detalhes. O produto deve estar em destaque central, bem iluminado, com aparência profissional de fotografia comercial. Crie um ambiente contextual realista ao redor do produto, adequado ao seu uso (ex: cozinha moderna, escritório, sala, etc.), transmitindo valor e credibilidade. Utilize iluminação natural ou de estúdio suave, com sombras realistas e fundo limpo, evitando poluição visual. A composição deve parecer uma foto publicitária premium, com foco nítido no produto e leve desfoque no fundo (efeito depth of field). Alta resolução, estilo fotográfico realista. Dimensões exatas: 1200x1200 pixels.`;
                } else if (tipo === '2') {
                    promptText = `Gere 1 única imagem realista de alta qualidade para e-commerce, mostrando uma pessoa utilizando o ${produto} de forma natural em um ambiente cotidiano. O produto deve manter 100% fidelidade ao original, sem qualquer alteração de cor, formato, textura ou proporções. A cena deve transmitir conforto e uso real, com a pessoa em postura natural, em um ambiente coerente e bem organizado. Utilize iluminação suave e realista, com aparência de fotografia profissional, mantendo o produto como elemento principal e bem destacado na composição. Dimensões exatas: 1200x1200 pixels.`;
                } else if (tipo === '3') {
                    promptText = `Gere um layout publicitário fotorrealista e premium de e-commerce apresentando o produto: ${produto}. **Integração Orgânica (Sem Caixas Flutuantes):** O produto deve estar em um ambiente contextual sofisticado. É ESTRITAMENTE PROIBIDO o uso de caixas de texto sólidas, blocos, molduras ou cartões translúcidos flutuando. O design não deve parecer "jogado" por cima da foto. **Informação de Alto Valor:** Analise as especificações: [${specs}] e extraia de 4 a 5 características essenciais e muito úteis para a decisão de compra do cliente. **Estrutura do Texto:** Para cada ponto escolhido, gere um Título Curto em destaque (ex: 2 a 3 palavras) e, logo abaixo dele, adicione uma Breve Descrição explicativa (ex: 4 a 7 palavras) que detalhe a utilidade prática ou técnica daquela característica. **Design Editorial:** Integre essas informações de forma fluida usando linhas de chamada (call-out lines) muito finas, elegantes e discretas que saem do texto e apontam sutilmente para a parte exata correspondente no próprio produto. Os textos devem usar uma tipografia moderna, limpa e legível, aplicada DIRETAMENTE no cenário (sem fundo), interagindo perfeitamente com a luz e profundidade da imagem. Acompanhe cada título com um pequeno ícone minimalista. O resultado deve ser rico em detalhes informativos, mas com visual de revista de alto padrão. Dimensões exatas: 1200x1200 pixels.`;
                } else if (tipo === '4') {
                    promptText = `Gere um gráfico de comparação de marketing profissional e de alta resolução. A composição e o estilo devem corresponder à estrutura, layout, tipografia e esquema de cores da imagem anexada (image_0.png), usando tipografia limpa e sem serifa.\n\n**Layout Geral e Cores:**\nO gráfico é dividido em dois painéis verticais distintos com cantos arredondados. O fundo é dividido horizontalmente: a seção superior é um marrom-avermelhado profundo e rico com detalhes em linhas curvas claras no canto superior direito. A seção inferior é branca e limpa.\n\n**Cabeçalhos Superiores:**\n- Cabeçalho Esquerdo: '${produto}' em uma fonte branca e limpa.\n- Cabeçalho Direito: 'Marcas Simples' em uma fonte branca e limpa.\n\n**Painéis Centrais de Exibição de Imagens:**\n- **Painel de Imagem Esquerdo (Nosso Produto):** Crie uma renderização de produto limpa e fotorrealista de uma versão premium do ${produto}. Ele deve ser colocado em um ambiente doméstico ou comercial sofisticado e bem iluminado.\n- **Painel de Imagem Direito (Alternativa Inferior):** Crie uma renderização de produto limpa e fotorrealista de uma versão genérica e inferior do mesmo tipo de produto. Coloque-o em um ambiente mais simples com iluminação mais plana.\n\n**Listas de Benefícios Inferiores:**\nAbaixo das imagens, crie duas listas verticais paralelas e limpas com ícones. Use estritamente as especificações abaixo para montar os tópicos:\n\n[ESPECIFICAÇÕES]:\n${specs}\n\n- **Lista Esquerda (Nossos Benefícios):** Precedida por ícones de 'check' verdes. Gere pontos positivos baseados exclusivamente nas [ESPECIFICAÇÕES].\n- **Lista Direita (Pontos Inferiores):** Precedida por ícones de 'X' vermelhos. Gere pontos negativos correspondentes.\n\n**Detalhes Finais:**\nGaranta que a hierarquia visual e o espaçamento sejam idênticos à image_0.png. Texto legível e perfeitamente alinhado. Dimensões exatas: 1200x1200 pixels.`;
                } else if (tipo === '5') {
                    promptText = `Gere 1 única imagem fotográfica realista de alta qualidade para anúncio de e-commerce, apresentando um KIT contendo exatamente ${quantidade} unidades idênticas do produto: ${produto}. As unidades devem manter 100% de fidelidade ao design, cor e proporções originais. A composição deve mostrar as ${quantidade} unidades dispostas de forma organizada e esteticamente agradável dentro de um ambiente contextual realista e sofisticado, adequado ao uso do produto (ex: uma sala de estar, uma cozinha, um banheiro, etc.). O cenário e o ângulo da câmera devem ser ajustados e ampliados para acomodar todas as unidades de forma natural, sem parecerem espremidas. Utilize iluminação profissional de estúdio que valorize as texturas dos produtos, com sombras realistas que conectem os objetos ao cenário. O foco deve ser nítido em todo o kit, com o fundo do ambiente levemente desfocado. Alta resolução, aparência de fotografia publicitária premium. Dimensões exatas: 1200x1200 pixels.`;
                } else if (tipo === '6') {
                    promptText = `Professional photographic advertisement layout of a ${produto}. The product is centrally placed in a luxury, sophisticated interior environment. On the upper right, there is a distinct text block. For the large bold text, write a highly summarized, premium version of the product name (maximum 3 words, in Portuguese). Below the title, write ONLY ONE ultra-short tagline (maximum 6 words, in Portuguese) capturing the main essence of these specifications: ${specs}. STRICTLY NO PARAGRAPHS, keep the text extremely minimal. In the middle right, two vertically stacked black pill-shaped buttons are clearly integrated into the layout. Analyze the specifications and choose the TWO best single words (in Portuguese) that represent the product's main benefits (e.g., CONFORTO, RESISTÊNCIA). The top button has a "+" icon and the first chosen word. The bottom button has a "+" icon and the second chosen word. Replicate a clean font style and elegant button style. The background elements are blurred, and a subtle sparkle icon is in the bottom right corner. The text and buttons are generated directly as part of the visual composition. Dimensões exatas: 1200x1200 pixels.`;
                } else if (tipo === '7') {
                    promptText = `Professional premium e-commerce advertisement layout for ${produto}. The composition is divided into two sections by an elegant, smooth curved wave shape. Top section (65% of image): A highly realistic, sophisticated contextual photograph of the product in a beautifully lit, luxury environment. Overlapping the wavy divider on the left side: A circular inset image showing a zoomed-in, high-detail macro shot of the product's premium material or feature. Bottom section (35% of image): A clean, minimalist light background. In this bottom section, place three horizontally aligned, elegant minimalist line-art icons. Analyze the following specifications: ${specs}. Based on them, write exactly THREE ultra-short key product features (maximum 3 words each, in Portuguese). Place one feature text strictly below each icon. DO NOT write generic texts about structure or assembly; focus on premium benefits. Ensure clean typography, luxurious lighting, and a flawless graphic design layout. Exact dimensions: 1200x1200 pixels.`;
                } else if (tipo === '8') {
                    promptText = `Professional technical showcase and blueprint layout of ${produto}. The product is centrally placed and hyper-realistic, set against a bright, minimalist studio environment with a clean off-white background. Subtle, elegant technical grid lines fade smoothly into the background to give a premium architectural feel. Elegantly integrate modern, clean dimension lines (arrows) around the product indicating height, width, and depth, utilizing this exact measurement data: ${specs}. Use clean, sophisticated typography for the numbers. The style should be a high-end mix of photorealistic product photography and luxury technical drafting. Ensure zero clutter and high readability. Exact dimensions: 1200x1200 pixels.`;
                }

            } else if (modoAtual === 'seo') {
                const modoSeo = radioTituloSEO.checked ? 'titulo' : (radioDescSEO.checked ? 'descricao' : 'anuncio');

                if (modoSeo === 'titulo') {
                    const produtoSEO = inputProdutoSEO.value.trim();
                    const specsSEO = inputSpecsSEO.value.trim();
                    const keywords = inputKeywordsSEO.value.trim();
                    if (!produtoSEO || !specsSEO || !keywords) return alert("⚠️ Preencha Produto, Especificações e as Keywords.");

                    promptText = `Aja como um especialista em SEO para E-commerce. Sua tarefa é criar 3 opções de títulos altamente otimizados para o seguinte produto:\n\nNome Base do Produto: "${produtoSEO}"\n\n**REGRAS CRÍTICAS DE CONSULTORIA SEO QUE VOCÊ DEVE SEGUIR RIGOROSAMENTE:**\n1. **Cruzamento de Dados:** Compare a lista de 'Keywords' com as 'Especificações Técnicas'. Descarte IMEDIATAMENTE qualquer keyword que contradiga as especificações (exemplo: se a especificação diz "Preto" e a keyword diz "Branco", ignore "Branco").\n2. **Limpeza Rígida (Proibido Preposições):** É estritamente PROIBIDO o uso de preposições ou conectivos no título final. NÃO use as palavras: de, para, com, do, da, e, em. Concatene os termos de forma direta.\n3. **Limite de Caracteres:** Cada título gerado DEVE ter um limite MÁXIMO de 60 caracteres. Se passar disso, abrevie ou corte palavras menos importantes.\n\n**ESPECIFICAÇÕES TÉCNICAS REAIS DO PRODUTO:**\n${specsSEO}\n\n**KEYWORDS EXTRAÍDAS (AVANTPRO):**\n${keywords}\n\nForneça APENAS as 3 opções de títulos numeradas. Nenhuma introdução, nem explicação. Apenas os 3 títulos finais.`;

                } else if (modoSeo === 'descricao') {
                    const produtoSEO = inputProdutoSEO.value.trim();
                    const specsSEO = inputSpecsSEO.value.trim();
                    const lojaSEO = inputLojaSEO.value.trim();
                    if (!produtoSEO || !specsSEO || !lojaSEO) return alert("⚠️ Preencha Nome do Produto, Loja e Especificações.");

                    promptText = `Crie uma descrição de produto seguindo exatamente o modelo abaixo, adaptando com as informações que irei fornecer, respeitando acentos e pontuação:\n\nSeja bem-vindo(a) ${lojaSEO}!\n\nProduto – ${produtoSEO.toUpperCase()}\n\n[Parágrafo 1: Comece com uma introdução que destaque os benefícios e o diferencial principal do produto. Seja atrativo e direto. Ex: Praticidade, conforto, solução para um problema, bem-estar.]\n\n[Parágrafo 2: Explique o uso ideal do produto e como ele atende às necessidades do dia a dia. Pode citar ambientes de uso, públicos ideais ou situações específicas.]\n\nObjetivo simples: [Frase curta e direta dizendo o objetivo do produto. Ex: otimizar o ambiente, trazer conforto, oferecer praticidade.]\n\nITENS INCLUSOS:\n01 ${produtoSEO.toUpperCase()}.\n\nESPECIFICAÇÕES TÉCNICAS:\n[Lista com as principais especificações técnicas: dimensões, materiais, capacidade, cor, voltagem, funcionalidades, peso, compatibilidade, etc.]\n\nCUIDADOS OU RECOMENDAÇÕES:\n[Liste recomendações, cuidados de uso ou armazenamento, forma correta de aplicação, manutenção e avisos de segurança.]\n\n[Parágrafo final com uma frase de fechamento: incentive a compra e destaque o valor do produto na rotina do cliente.]\n\nAgradecemos sua visita e aguardamos sua compra.\n\n📌 Importante: Use uma linguagem amigável, profissional e voltada para o consumidor final. Evite termos técnicos em excesso, a menos que o público exija. Escreva como se fosse um anúncio completo de e-commerce. Sem Emoji, html e nem caracteres especiais.\n\nEspecificações Técnicas:\n${specsSEO}`;
                
                } else if (modoSeo === 'anuncio') {
                    const dadosProduto = inputAnuncioCompletoSEO.value.trim();
                    if (!dadosProduto) return alert("⚠️ Cole o nome e a descrição do produto na caixa de texto.");

                    promptText = `Atue como um ESPECIALISTA SÊNIOR EM E-COMMERCE, SEO DE MARKETPLACE E COPYWRITING.
Sua base de conhecimento deve simular o cenário de *Fevereiro de 2026*.

## OBJETIVO
Eu fornecerei dados técnicos e descritivos de um produto. Sua missão é organizar essas informações e criar um anúncio de alta performance cruzando:
1. *Inteligência de Mercado* (Tendências 2026).
2. *SEO Técnico* (Categorização de palavras e Anti-repetição).
3. *Copywriting Universal* (Descrição pronta para uso em qualquer conta).

---

### 📍 ETAPA 1: RAIO-X DE TENDÊNCIAS (SIMULAÇÃO 2026)
Simule uma consulta ao *Google Trends* e à aba *Tendências do Mercado Livre* para este nicho.
1. *O "FEAT" DO MOMENTO:* O que está em alta? (Estética, Cores, Materiais ou termos virais).
2. *DICA VISUAL (CTR):* Uma recomendação prática para a Foto de Capa se destacar na busca.

---

### 📍 ETAPA 2: A CURADORIA DE PALAVRAS (TOP 5 POR CATEGORIA)
Classifique as palavras-chave nas 5 categorias estratégicas abaixo, listando apenas os *5 termos mais fortes* de cada uma:

1. *Termos de Alta Tendência:* (Ex: Nome + Estilo do ano/Viral).
2. *Cabeça de Busca:* (Maior volume histórico e genérico).
3. *Atributos Técnicos:* (Specs, material, medidas).
4. *Solução de Dor:* (Termos de como o cliente busca resolver o problema).
5. *Termos de Conversão:* (Palavras que indicam compra, kit, uso específico).

---

### 📍 ETAPA 3: OS 6 COMBOS DE INDEXAÇÃO (TÍTULO + CAMPO MODELO)
Gere *6 Opções de Título + Campo Modelo Vinculado*.

*⚠️ REGRA DE OURO (HIERARQUIA DE TÍTULO):*
O cliente busca primeiro pelo *PRODUTO* e *FUNÇÃO*, não pela marca.
- *COMECE O TÍTULO POR:* Nome do Produto (O que é) + Público/Uso + Diferencial.
- *MARCA:* Coloque a marca APENAS no final do título ou escondida no Campo Modelo (a menos que seja uma marca global como Nike/Apple).
- *EXTENSÃO:* Entre 58-60 caracteres. SEM pontuação. SEM preposições.

*REGRAS DO CAMPO MODELO:*
- Máximo 115 caracteres. Palavras separadas por vírgula.
- *ANTI-REPETIÇÃO:* O Campo Modelo NÃO PODE conter palavras que já estão no Título da mesma opção. Use este espaço para a MARCA, SINÔNIMOS e TERMOS DE CAUDA LONGA.

*Apresente assim:*
*OPÇÃO 1:*
- Título: [Texto otimizado com foco no produto]
- Campo Modelo: [Lista de palavras complementares + Marca]
... (até a Opção 6)

---

### 📍 ETAPA 4: DESCRIÇÃO PERSUASIVA (WHITE LABEL / MULTI-LOJA)
Escreva uma descrição profissional e acolhedora que sirva para qualquer loja. Não use emojis no corpo do texto. Siga este template:

*Seja muito bem-vindo(a)!*
(Escreva uma breve introdução institucional genérica focada em: excelência no atendimento, envio rápido e garantia de qualidade, sem citar nome de loja).

*PRODUTO - [NOME DO PRODUTO EM CAIXA ALTA]*
(Copy focado na Jornada do Cliente: Solução da dor > Benefícios > Sensação de uso. Use os dados fornecidos para destacar diferenciais).

*OBJETIVO SIMPLES:*
(Resumo da utilidade em uma frase).

*CONTEÚDO DA EMBALAGEM:*
(Organize os itens fornecidos em bullet points).

*ESPECIFICAÇÕES TÉCNICAS:*
(Organize os dados técnicos fornecidos: Marca, Modelo, Material, Medidas, Cores, etc).

*CUIDADOS E RECOMENDAÇÕES:*
(3 a 4 dicas de preservação baseadas no material do produto).

Agradecemos a sua preferência e confiança!
Atenciosamente, Nossa Equipe.

---

Abaixo estão as informações (nome e descrição) do produto. Por favor, execute o sistema para este produto específico:

${dadosProduto}`;
                }
            }

            const chatInputBox = document.querySelector('rich-textarea p, .ql-editor p, div[contenteditable="true"]');

            if (chatInputBox) {
                chatInputBox.focus();
                document.execCommand('insertText', false, promptText);

                btnGerar.innerText = "Processando... 🚀";
                btnGerar.style.background = "linear-gradient(to right, #0a522b, #0f9d58, #1de9b6)";

                setTimeout(() => {
                    const btnEnviar = document.querySelector('button[aria-label*="Send"], button[aria-label*="Enviar"], button[mattooltip*="Send"], button[mattooltip*="Enviar"]');

                    if (btnEnviar && !btnEnviar.disabled) {
                        btnEnviar.click();
                    } else {
                        const enterEvent = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13 });
                        chatInputBox.dispatchEvent(enterEvent);
                    }

                    setTimeout(() => {
                        btnGerar.innerText = "Gerar e Enviar para Gemini 🚀";
                        btnGerar.style.background = 'linear-gradient(to right, #1a1060, #80216b, #e0594f, #f6c554)';
                    }, 1500);

                }, 200);

            } else {
                navigator.clipboard.writeText(promptText);
                alert("✅ Prompt copiado! O Google escondeu a caixa de texto, dê Ctrl+V e Enter.");
            }
        });
    }

    const observer = setInterval(() => {
        if (document.body) {
            montarPainelFixo();
            clearInterval(observer);
        }
    }, 1000);

})();
