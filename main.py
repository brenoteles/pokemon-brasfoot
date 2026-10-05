import asyncio
import pandas as pd
import re
import json
import plotly.express as px
from poke_env.player import SimpleHeuristicsPlayer
import times  # Arquivo com as variáveis player_1...player_100

# --- GERADOR DE DASHBOARD HTML (CSS GRID MULTI-CHART) ---
def gerar_dashboard_html(df_leaderboard, df_h2h, df_pkm_global, df_moves, df_traits):
    print("🎨 Renderizando Dashboard Full-Stack (10 Gráficos)...")
    html_components = []

    # Pre-processamento de métricas avançadas com proteção contra div/0 e dfs vazios
    if not df_pkm_global.empty:
        df_pkm_global["Taxa de Sobrevivência (%)"] = (100 - (df_pkm_global["Total_Mortes"] / df_pkm_global["Total_Games"] * 100)).round(2).fillna(0)
    else:
        df_pkm_global["Taxa de Sobrevivência (%)"] = pd.Series(dtype=float)
        
    df_leaderboard["Perfil"] = df_leaderboard["KOs Feitos"] / (df_leaderboard["KOs Sofridos"] + 1)

    # 1. Scatter: Meta de Pokémon (Uso vs Win Rate)
    fig1 = px.scatter(df_pkm_global.head(60), x="Total_Games", y="Taxa de Vitória (%)", size="Total_Vitorias" if not df_pkm_global.empty else None, 
                      color="Taxa de Vitória (%)", hover_name="Pokemon", title="1. Meta Core: Frequência vs Eficiência",
                      color_continuous_scale="Plotly3", template="plotly_dark")
    fig1.add_hline(y=50, line_dash="dash", line_color="red")
    html_components.append(f'<div class="chart-container full-width">{fig1.to_html(full_html=False, include_plotlyjs="cdn")}</div>')

    # 2. Ranking de Elo (Top 50)
    fig2 = px.bar(df_leaderboard.head(50), x="Nome", y="Elo", color="Taxa de Vitória (%)", 
                  title="2. Leaderboard: Top 50 Elos", template="plotly_dark", color_continuous_scale="Viridis")
    html_components.append(f'<div class="chart-container">{fig2.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 3. Histograma: Distribuição de Elo do Torneio
    fig3 = px.histogram(df_leaderboard, x="Elo", marginal="box", title="3. Curva de Habilidade (Distribuição de Elo)", 
                        color_discrete_sequence=['#ab63fa'], template="plotly_dark")
    html_components.append(f'<div class="chart-container">{fig3.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 4. Matriz de Agressividade (KOs Feitos vs Sofridos)
    fig4 = px.scatter(df_leaderboard, x="KOs Feitos", y="KOs Sofridos", color="Elo", hover_name="Nome",
                      title="4. Perfil de Combate: Offense vs Stall", template="plotly_dark", color_continuous_scale="Inferno")
    html_components.append(f'<div class="chart-container">{fig4.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 5. Histograma: Distribuição de Win Rate
    fig5 = px.histogram(df_leaderboard, x="Taxa de Vitória (%)", nbins=20, title="5. Saúde do Torneio: Win Rates", 
                        color_discrete_sequence=['#00cc96'], template="plotly_dark")
    html_components.append(f'<div class="chart-container">{fig5.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 6. Scatter: Meta Oculto de Moves
    max_games = df_moves['Games'].max() if not df_moves.empty else 0
    df_moves_filtered = df_moves[df_moves['Games'] > (max_games * 0.05)] if not df_moves.empty else df_moves
    fig6 = px.scatter(df_moves_filtered, x="Games", y="Taxa de Vitória (%)", hover_name=df_moves_filtered.index if not df_moves_filtered.empty else None,
                      title="6. Meta Completo: Eficiência de Ataques (Reveal All)", color="Taxa de Vitória (%)", template="plotly_dark")
    fig6.add_hline(y=50, line_dash="dash", line_color="gray")
    html_components.append(f'<div class="chart-container">{fig6.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 7. Ranking: Moves Mais Presentes (Top 20)
    fig7 = px.bar(df_moves.head(20), x=df_moves.head(20).index if not df_moves.empty else None, y="Games", color="Taxa de Vitória (%)",
                  title="7. Meta Rate: Top 20 Moves Mais Presentes nas Equipes", template="plotly_dark", color_continuous_scale="Bluered")
    html_components.append(f'<div class="chart-container">{fig7.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 8. Treemap: Combinações de Habilidade/Item
    fig8 = px.treemap(df_traits.head(40), path=[px.Constant("Traits"), 'Habilidade', 'Item'], values='Games',
                      color='Taxa de Vitória (%)', color_continuous_scale='RdBu', title="8. Diversidade de Traits (Item + Ability)", template="plotly_dark")
    html_components.append(f'<div class="chart-container">{fig8.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 9. Ranking: Taxa de Sobrevivência (Top 20 Pokémon)
    top_survivors = df_pkm_global[df_pkm_global['Total_Games'] > 10].sort_values(by="Taxa de Sobrevivência (%)", ascending=False).head(20) if not df_pkm_global.empty else df_pkm_global
    fig9 = px.bar(top_survivors, x="Pokemon", y="Taxa de Sobrevivência (%)", color="Total_Games",
                  title="9. Imortais: Maior Taxa de Sobrevivência por Jogo", template="plotly_dark")
    html_components.append(f'<div class="chart-container">{fig9.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # 10. Heatmap H2H (Elite Top 50) [FULL WIDTH]
    limite_h2h = min(50, len(df_leaderboard))
    top_50_nomes = df_leaderboard.head(limite_h2h)["Nome"].tolist()
    if not df_h2h.empty:
        df_h2h_elite = df_h2h.loc[df_h2h.index.intersection(top_50_nomes), df_h2h.columns.intersection(top_50_nomes)]
    else:
        df_h2h_elite = pd.DataFrame()
        
    fig10 = px.imshow(df_h2h_elite, aspect="auto", color_continuous_scale="RdBu_r", 
                      title=f"10. Matriz H2H Elite Top {limite_h2h} (Rivalidades)", template="plotly_dark")
    fig10.update_layout(height=800)
    html_components.append(f'<div class="chart-container full-width">{fig10.to_html(full_html=False, include_plotlyjs=False)}</div>')

    # --- MONTAGEM HTML COM CSS GRID ---
    dashboard_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Showdown Analytics Engine</title>
        <style>
            body {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 30px; }}
            h1 {{ text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 20px; color: #58a6ff; font-size: 2.5em; }}
            .stats-bar {{ display: flex; justify-content: space-around; background: #161b22; padding: 20px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #30363d; flex-wrap: wrap; gap: 20px; }}
            .stats-box {{ text-align: center; min-width: 200px; }}
            .stats-box h3 {{ margin: 0; color: #8b949e; font-size: 1em; text-transform: uppercase; }}
            .stats-box p {{ margin: 10px 0 0 0; font-size: 2em; font-weight: bold; color: #fff; }}
            .dashboard-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 25px; }}
            .chart-container {{ background-color: #161b22; padding: 15px; border-radius: 12px; border: 1px solid #30363d; box-shadow: 0 4px 15px rgba(0,0,0,0.3); overflow: hidden; }}
            .full-width {{ grid-column: span 2; }}
            @media (max-width: 1200px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} .full-width {{ grid-column: span 1; }} }}
        </style>
    </head>
    <body>
        <h1>🔥 Showdown Data Engineering Dashboard</h1>
        <div class="stats-bar">
            <div class="stats-box"><h3>Jogadores Analisados</h3><p>{len(df_leaderboard)}</p></div>
            <div class="stats-box"><h3>KOs Registrados</h3><p>{df_leaderboard['KOs Feitos'].sum() if not df_leaderboard.empty else 0}</p></div>
            <div class="stats-box"><h3>Moves Únicos na Pool</h3><p>{len(df_moves)}</p></div>
            <div class="stats-box"><h3>Maior Elo Atingido</h3><p>{df_leaderboard['Elo'].max() if not df_leaderboard.empty else 0}</p></div>
        </div>
        <div class="dashboard-grid">
            {''.join(html_components)}
        </div>
    </body>
    </html>
    """

    with open("Showdown_Analytics_Pro.html", "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    print("🎇 Dashboard interativo PRO salvo como 'Showdown_Analytics_Pro.html'!")


# --- SISTEMA ELO ---
def calcular_elo(elo_a: int, elo_b: int, vitorias_a: int, vitorias_b: int, k: int = 32) -> tuple:
    total_jogos = vitorias_a + vitorias_b
    resultado_a = vitorias_a / total_jogos if total_jogos > 0 else 0.5
    expectativa_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    expectativa_b = 1 / (1 + 10 ** ((elo_a - elo_b) / 400))
    novo_elo_a = elo_a + k * (resultado_a - expectativa_a)
    novo_elo_b = elo_b + k * ((1 - resultado_a) - expectativa_b)
    return round(novo_elo_a), round(novo_elo_b)

# --- PAREAMENTO MODO LADDER ---
def gerar_pares_ladder(jogadores: list, tabela_stats: dict) -> list:
    jogadores_ordenados = sorted(
        jogadores, 
        key=lambda p: tabela_stats[p.bot_id]["Elo"], 
        reverse=True
    )
    pares = []
    for i in range(0, len(jogadores_ordenados) - 1, 2):
        pares.append((jogadores_ordenados[i], jogadores_ordenados[i+1]))
    return pares

# --- EXTRATOR DE DADOS TOTAIS (REVEAL ALL) ---
def extrair_stats_full_reveal(player, batalha_time: dict, ganhou: bool, db_pkm: dict, db_moves: dict, db_traits: dict):
    nome_jogador = player.bot_id
    vit = 1 if ganhou else 0
    kos_sofridos = 0

    mortes_por_especie = {}
    if batalha_time:
        for mon in batalha_time.values():
            esp_clean = re.sub(r'[^a-z0-9]', '', mon.species.lower())
            mortes_por_especie[esp_clean] = 1 if mon.fainted else 0
            if mon.fainted:
                kos_sofridos += 1

    for mon in player.teambuilder_pokemon:
        esp = mon.species
        esp_clean = re.sub(r'[^a-z0-9]', '', esp.lower())
        hab = mon.ability if mon.ability else "Desconhecida"
        item = mon.item if mon.item else "Desconhecido"

        morto = mortes_por_especie.get(esp_clean, 0)
        
        chave_pkm = f"{nome_jogador}|{esp}"
        if chave_pkm not in db_pkm:
            db_pkm[chave_pkm] = {"Jogador": nome_jogador, "Pokemon": esp, "Games": 0, "Vitorias": 0, "Mortes": 0}
        db_pkm[chave_pkm]["Games"] += 1
        db_pkm[chave_pkm]["Vitorias"] += vit
        db_pkm[chave_pkm]["Mortes"] += morto

        for move_id in mon.moves:
            if not move_id: continue
            move_id_clean = re.sub(r'[^a-z0-9]', '', move_id.lower())
            if move_id_clean not in db_moves:
                db_moves[move_id_clean] = {"Move": move_id_clean, "Games": 0, "Vitorias": 0}
            db_moves[move_id_clean]["Games"] += 1
            db_moves[move_id_clean]["Vitorias"] += vit

        chave_trait = f"{esp}|{hab}|{item}"
        if chave_trait not in db_traits:
            db_traits[chave_trait] = {"Pokemon": esp, "Habilidade": hab, "Item": item, "Games": 0, "Vitorias": 0}
        db_traits[chave_trait]["Games"] += 1
        db_traits[chave_trait]["Vitorias"] += vit
        
    return kos_sofridos

# --- EXECUTOR DE BATALHA (MD3) ---
async def jogar_md3(p1, p2, semaforo: asyncio.Semaphore, num_rodada: int, db_pkm: dict, db_moves: dict, db_traits: dict):
    async with semaforo:
        vitorias_p1 = 0
        vitorias_p2 = 0
        kos_sofridos_p1_total = 0
        kos_sofridos_p2_total = 0
        
        while vitorias_p1 < 2 and vitorias_p2 < 2:
            v1_antes = p1.n_won_battles
            try:
                await asyncio.wait_for(p1.battle_against(p2, n_battles=1), timeout=60.0)
                
                ganhou_p1 = (p1.n_won_battles > v1_antes)
                if ganhou_p1:
                    vitorias_p1 += 1
                else:
                    vitorias_p2 += 1

                if p1.battles:
                    id_batalha = list(p1.battles.keys())[-1]
                    batalha = p1.battles[id_batalha]
                    
                    k_sof_p1 = extrair_stats_full_reveal(p1, batalha.team, ganhou_p1, db_pkm, db_moves, db_traits)
                    k_sof_p2 = extrair_stats_full_reveal(p2, batalha.opponent_team, not ganhou_p1, db_pkm, db_moves, db_traits)
                    
                    kos_sofridos_p1_total += k_sof_p1
                    kos_sofridos_p2_total += k_sof_p2
                else:
                    extrair_stats_full_reveal(p1, {}, ganhou_p1, db_pkm, db_moves, db_traits)
                    extrair_stats_full_reveal(p2, {}, not ganhou_p1, db_pkm, db_moves, db_traits)

            except asyncio.TimeoutError:
                break
            except Exception as e:
                vitorias_p1 = 2 if vitorias_p1 > vitorias_p2 else 0
                vitorias_p2 = 2 if vitorias_p2 > vitorias_p1 else 0
                break

        return p1.bot_id, p2.bot_id, vitorias_p1, vitorias_p2, kos_sofridos_p1_total, kos_sofridos_p2_total

# --- FLUXO PRINCIPAL ---
async def main():
    jogadores = []
    tabela = {}
    historico_confrontos = {} 
    db_pkm = {}
    db_moves = {}
    db_traits = {}
    
    CUSTOM_FORMAT = "gen9anythinggoescustom"
    MAX_RODADAS = 50   
    ELO_INICIAL = 1000  

    print("Carregando times no pipeline...")
    for i in range(1, 101): 
        var = f"player_{i}"
        if hasattr(times, var):
            team_str = getattr(times, var)
            p = SimpleHeuristicsPlayer(battle_format=CUSTOM_FORMAT, team=team_str, max_concurrent_battles=2000)
            
            id_seguro = f"Player {i}"
            p.bot_id = id_seguro 
            jogadores.append(p)
            
            tabela[id_seguro] = {
                "Nome": id_seguro,
                "Séries Jogadas": 0, "Vitórias": 0, "Derrotas": 0, 
                "Taxa de Vitória (%)": 0.0,
                "KOs Feitos": 0, "KOs Sofridos": 0, 
                "Elo": ELO_INICIAL
            }
            historico_confrontos[id_seguro] = {}
        else: 
            break

    if not jogadores:
        print("Nenhum jogador carregado.")
        return

    limite_pc = asyncio.Semaphore(1000)
    print(f"🏆 Rodando torneio com {len(jogadores)} jogadores. Rodadas: {MAX_RODADAS}")

    for rodada in range(1, MAX_RODADAS + 1):
        print(f"Gerando pareamentos e processando Rodada {rodada}/{MAX_RODADAS}...")
        pares_rodada = gerar_pares_ladder(jogadores, tabela)
        
        tarefas = [jogar_md3(p1, p2, limite_pc, rodada, db_pkm, db_moves, db_traits) for p1, p2 in pares_rodada]
        resultados = await asyncio.gather(*tarefas)
        
        for u1, u2, v1, v2, kos_sof_1, kos_sof_2 in resultados:
            
            tabela[u1]["Séries Jogadas"] += 1
            tabela[u2]["Séries Jogadas"] += 1
            tabela[u1]["KOs Sofridos"] += kos_sof_1
            tabela[u1]["KOs Feitos"] += kos_sof_2  
            tabela[u2]["KOs Sofridos"] += kos_sof_2
            tabela[u2]["KOs Feitos"] += kos_sof_1

            if v1 > v2:
                tabela[u1]["Vitórias"] += 1
                tabela[u2]["Derrotas"] += 1
                historico_confrontos[u1].setdefault(u2, 0)
                historico_confrontos[u1][u2] += 1
            elif v2 > v1:
                tabela[u2]["Vitórias"] += 1
                tabela[u1]["Derrotas"] += 1
                historico_confrontos[u2].setdefault(u1, 0)
                historico_confrontos[u2][u1] += 1

            tabela[u1]["Elo"], tabela[u2]["Elo"] = calcular_elo(tabela[u1]["Elo"], tabela[u2]["Elo"], v1, v2)

    print("✅ Batalhas concluídas. Consolidando pipeline analítico...")

    # --- GARANTIA DE ESTRUTURA DOS DATAFRAMES (EVITA CRASHES SE ESTIVER VAZIO) ---

    df_leaderboard = pd.DataFrame.from_dict(tabela, orient='index')
    if not df_leaderboard.empty:
        df_leaderboard["Taxa de Vitória (%)"] = (df_leaderboard["Vitórias"] / (df_leaderboard["Séries Jogadas"].replace(0, 1)) * 100).round(2)
        df_leaderboard.sort_values(by=['Elo', 'Taxa de Vitória (%)'], ascending=[False, False], inplace=True)
    df_leaderboard.reset_index(drop=True, inplace=True)

    df_h2h = pd.DataFrame(historico_confrontos).fillna(0).astype(int)

    df_pkm = pd.DataFrame.from_dict(db_pkm, orient='index')
    if df_pkm.empty:
        df_pkm = pd.DataFrame(columns=["Jogador", "Pokemon", "Games", "Vitorias", "Mortes", "Taxa de Vitória (%)"])
    else:
        df_pkm["Taxa de Vitória (%)"] = (df_pkm["Vitorias"] / df_pkm["Games"] * 100).round(2)
        df_pkm.sort_values(by=["Jogador", "Taxa de Vitória (%)"], ascending=[True, False], inplace=True)

    if not df_pkm.empty:
        df_pkm_global = df_pkm.groupby('Pokemon').agg(
            Total_Games=('Games', 'sum'),
            Total_Vitorias=('Vitorias', 'sum'),
            Total_Mortes=('Mortes', 'sum')
        ).reset_index()
        df_pkm_global["Taxa de Vitória (%)"] = (df_pkm_global["Total_Vitorias"] / df_pkm_global["Total_Games"] * 100).round(2)
        df_pkm_global.sort_values(by="Total_Games", ascending=False, inplace=True)
    else:
        df_pkm_global = pd.DataFrame(columns=['Pokemon', 'Total_Games', 'Total_Vitorias', 'Total_Mortes', 'Taxa de Vitória (%)', 'Taxa de Sobrevivência (%)'])

    df_moves = pd.DataFrame.from_dict(db_moves, orient='index')
    if df_moves.empty:
        df_moves = pd.DataFrame(columns=["Move", "Games", "Vitorias", "Taxa de Vitória (%)"])
    else:
        df_moves["Taxa de Vitória (%)"] = (df_moves["Vitorias"] / df_moves["Games"] * 100).round(2)
        df_moves.sort_values(by="Games", ascending=False, inplace=True)

    df_traits = pd.DataFrame.from_dict(db_traits, orient='index')
    if df_traits.empty:
        df_traits = pd.DataFrame(columns=["Pokemon", "Habilidade", "Item", "Games", "Vitorias", "Taxa de Vitória (%)"])
    else:
        df_traits["Taxa de Vitória (%)"] = (df_traits["Vitorias"] / df_traits["Games"] * 100).round(2)
        df_traits.sort_values(by="Games", ascending=False, inplace=True)

    # --- GERANDO ARQUIVOS ---
    nome_arquivo = 'Dashboard_Analytics_Pokemon.xlsx'
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        df_leaderboard.to_excel(writer, sheet_name='🏆 Leaderboard', index=False)
        df_h2h.to_excel(writer, sheet_name='⚔️ Head-to-Head')
        df_pkm_global.to_excel(writer, sheet_name='📊 Stats PKM Geral', index=False)
        df_pkm.to_excel(writer, sheet_name='👥 PKM por Jogador', index=False)
        df_moves.to_excel(writer, sheet_name='💥 Meta de Moves', index=False)
        df_traits.to_excel(writer, sheet_name='🧬 Habilidades e Itens', index=False)

    print(f"📂 Arquivo Excel '{nome_arquivo}' gerado com sucesso!")
    
    print("💾 Exporting tournament state to JSON...")
    
    team_data = {}
    for i in range(1, 101):
        var_name = f"player_{i}"
        if hasattr(times, var_name):
            team_data[f"Player {i}"] = getattr(times, var_name)
    
    export_data = {
        "leaderboard": df_leaderboard.to_dict(orient="records"),
        "teams": team_data
    }
    
    with open("tournament_state.json", "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=4)
        
    print("✅ JSON export complete: 'tournament_state.json'")

    gerar_dashboard_html(df_leaderboard, df_h2h, df_pkm_global, df_moves, df_traits)

if __name__ == "__main__":
    asyncio.run(main())