import streamlit as st
from abc import ABC, abstractmethod
from dashboard.utils import format_rupiah

class BaseDashboard(ABC):
    def __init__(self, df):
        self.df = df

    @abstractmethod
    def filter_data(self):
        pass

    @abstractmethod
    def show_metrics(self):
        pass

    @abstractmethod
    def show_visualization(self):
        pass
    

    def run(self):
        self.filter_data()
        self.show_metrics()
        self.show_visualization()
        
