<<<<<<< HEAD
/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
  	extend: {
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		colors: {
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out'
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
};
=======
/**
 * tailwind.config.js
 *
 * Arquivo de configuração do TailwindCSS.
 * Aqui definimos:
 * - Onde o Tailwind deve procurar classes (content)
 * - Tema customizado (cores, radius, animações)
 * - Plugins adicionais
 *
 * ⚠️ Se for fazer manutenção no futuro:
 * - Alterações visuais globais (cores, radius, animações) devem ser feitas aqui.
 * - Evite colocar valores fixos nos componentes se já existir variável aqui.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  /**
   * Habilita modo escuro baseado em classe.
   * Para ativar dark mode:
   * <html class="dark">
   */
  darkMode: ["class"],

  /**
   * Arquivos onde o Tailwind vai procurar classes.
   * Se criar novas pastas (ex: components, layouts),
   * adicione aqui para não quebrar o purge.
   */
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],

  theme: {
    extend: {

      /**
       * Border radius customizado usando variável CSS (--radius).
       * Permite mudar o arredondamento global apenas alterando a variável.
       */
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },

      /**
       * Sistema de cores baseado em variáveis CSS (HSL).
       * Isso permite:
       * - Troca dinâmica de tema (light/dark)
       * - Fácil manutenção futura
       *
       * ⚠️ As variáveis (--background, --primary, etc.)
       * devem existir no CSS global (ex: index.css).
       */
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',

        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },

        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },

        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },

        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },

        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },

        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },

        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },

        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',

        /**
         * Cores específicas para gráficos.
         * Pode ser usado com bibliotecas de chart.
         */
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        }
      },

      /**
       * Animações personalizadas (usadas normalmente com Radix UI Accordion).
       * Controlam abertura e fechamento suave.
       */
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' }
        }
      },

      /**
       * Define como as animações serão usadas.
       * Duração: 0.2s
       * Easing: ease-out
       */
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out'
      }
    }
  },

  /**
   * Plugins extras do Tailwind.
   * tailwindcss-animate adiciona utilitários de animação.
   *
   * ⚠️ Se remover esse plugin, animações podem parar de funcionar.
   */
  plugins: [require("tailwindcss-animate")],
};
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
